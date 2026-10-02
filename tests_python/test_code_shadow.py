"""Shadow input isolation, one-batch reuse and failure behavior."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from codex_adaptive_agents import cli, code_shadow


class CodeShadowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name).resolve()
        self.home = self.project / 'home'
        monitor = self.home / 'laya-monitor' / 'monitor.py'
        monitor.parent.mkdir(parents=True)
        monitor.write_text('# test boundary only\n')
        self.input = self.project / 'tasks.jsonl'
        self.items = [dict(task_ref='fix-a', state='修复空输入，保留现有接口并检查边界。\n只改对应函数。',
                           efforts=['xhigh', 'medium', 'high'], actual_role='adaptive_luna_high'),
                      dict(task_ref='review-b', state='只读核对调用方是否兼容新接口；交付具体位置与证据。',
                           efforts=['low', 'high'], actual_role='adaptive_luna_low')]
        self.write()

    def write(self):
        self.input.write_text(''.join(json.dumps(item, ensure_ascii=False) + '\n' for item in self.items))

    def test_batch_isolates_actual_choice_and_reuses_observation(self):
        observed = []

        def boundary(command, **kwargs):
            observed.append(command)
            self.assertEqual(kwargs['env']['LAYA_CALLER'], 'codex')
            self.assertEqual(command[2], str(self.home / 'laya-monitor' / 'monitor.py'))
            source = Path(command[command.index('--input') + 1])
            if 'consult' not in command:
                events = json.loads(source.read_text())
                self.assertEqual(len(events), 4)
                self.assertTrue(all(e['adoption'] == 'not_applicable' and
                                    e['decision_changed'] is False and 'assessment' not in e for e in events))
                self.assertEqual([e['actual_choice'] for e in events if 'actual_choice' in e], ['high', 'low'])
                return subprocess.CompletedProcess(command, 0, b'{}\n', b'')
            model_inputs = [json.loads(line) for line in source.read_text().splitlines()]
            contexts = json.loads(Path(command[command.index('--context') + 1]).read_text())['items']
            self.assertEqual([c['baseline_choice'] for c in contexts], ['high', 'low'])
            self.assertNotIn('actual_role', source.read_text())
            self.assertNotIn('baseline_choice', source.read_text())
            self.assertEqual(model_inputs[0]['state'], self.items[0]['state'])
            self.assertEqual(model_inputs[0]['questions']['effort']['criteria'], ['medium', 'high', 'xhigh'])
            rows = [dict(id=value['id'], line=i, ok=True, advisory_only=True, execution_authorized=False,
                         answers={'readiness': {}, 'effort': {}},
                         tracking=dict(captured=True, call_id='call-' + str(i), task_key='task-' + str(i),
                                       question_ids={'readiness': 'q-ready-' + str(i), 'effort': 'q-effort-' + str(i)}))
                    for i, value in enumerate(model_inputs, 1)]
            return subprocess.CompletedProcess(command, 0,
                ''.join(json.dumps(row) + '\n' for row in rows).encode(), b'')

        with patch.object(code_shadow, 'run', side_effect=boundary):
            result = code_shadow.observe(self.home, self.project, self.input, 'verification')
            self.assertEqual(result['status'], 'SHADOW_RECORDED')
            self.assertTrue(result['observation_recorded'])
            self.items.reverse()
            self.write()
            repeated = code_shadow.observe(self.home, self.project, self.input, 'verification')
            self.assertTrue(repeated['cached'])
            self.assertEqual(len(observed), 2)  # One inference process, one append-only event submission.
            self.items[1]['actual_role'] = 'adaptive_luna_medium'
            self.write()
            with self.assertRaisesRegex(ValueError, 'different dispatch metadata'):
                code_shadow.observe(self.home, self.project, self.input, 'verification')
            self.assertEqual(len(observed), 2)

    def test_failure_and_incomplete_attempt_do_not_repeat_inference(self):
        with patch.object(code_shadow, 'run', side_effect=RuntimeError('command timed out')) as boundary:
            result = code_shadow.observe(self.home, self.project, self.input, 'verification')
            self.assertEqual(result['status'], 'SHADOW_FAILED')
            self.assertFalse(result['execution_authorized'])
            self.assertTrue(code_shadow.observe(self.home, self.project, self.input, 'verification')['cached'])
            Path(result['snapshot']).with_name('result.json').unlink()
            interrupted = code_shadow.observe(self.home, self.project, self.input, 'verification')
            self.assertEqual(interrupted['status'], 'SHADOW_INCOMPLETE')
            self.assertEqual(boundary.call_count, 1)

    def test_invalid_candidate_rejects_before_local_inference_or_state_write(self):
        self.items[0]['actual_role'] = 'other-model'
        self.write()
        with patch.object(code_shadow, 'run') as boundary:
            with self.assertRaises(ValueError):
                code_shadow.observe(self.home, self.project, self.input, 'production')
            boundary.assert_not_called()
        self.assertFalse((self.project / '.codex-adaptive-agents').exists())

    def test_cli_missing_monitor_and_local_failure_are_best_effort(self):
        for home, effect in [(self.project / 'missing', None), (self.home, RuntimeError('resource is locked'))]:
            with self.subTest(home=home), redirect_stdout(StringIO()) as output:
                arguments = ['--codex-home', str(home), 'code-shadow', '--project', str(self.project),
                             '--input', str(self.input), '--purpose', 'verification']
                if effect:
                    with patch.object(code_shadow, 'observe', side_effect=effect):
                        self.assertEqual(cli.main(arguments), 0)
                else:
                    self.assertEqual(cli.main(arguments), 0)
                result = json.loads(output.getvalue())
                self.assertIn(result['status'], ('SHADOW_UNAVAILABLE', 'SHADOW_FAILED'))
                self.assertFalse(result['execution_authorized'])
                self.assertFalse(result['decision_changed'])

    def test_all_routes_record_without_models_and_append_outcomes_idempotently(self):
        self.items = [
            dict(task_ref='direct', state='已定位的一次局部修改。', reason='交接比直接修改成本高。',
                 executor=dict(kind='main', model='current-model')),
            dict(task_ref='native', state='明确、独立且有现成检查的实现包。', reason='原生交接足够。',
                 executor=dict(kind='luna', model='gpt-6-luna', role='adaptive_luna_medium', execution_id='fixture-child')),
            dict(task_ref='workbench', state='需要已接入执行器的独立任务。', reason='用户指定的执行器在工作台。',
                 executor=dict(kind='workbench', model='fixture-model', agent_id='fixture-agent',
                               provider_id='fixture-provider', execution_id='fixture-task')),
            dict(task_ref='research', state='独立核对原始资料，返回出处。', reason='宿主原生代理可执行，模型未披露。',
                 executor=dict(kind='native', model='unknown', execution_id='/root/fixture-research'))]
        self.write()
        with patch.object(code_shadow, 'run') as boundary:
            first = code_shadow.record(self.project, self.input, 'verification')
            self.assertEqual(first['status'], 'CODE_RECORDED')
            self.assertFalse(first['execution_started'])
            generic = next(row for row in first['records'] if row['task_ref'] == 'research')
            event = json.loads(Path(generic['record']).read_text())
            self.assertEqual(event['executor'], self.items[3]['executor'])
            repeated = code_shadow.record(self.project, self.input, 'verification')
            self.assertTrue(all(row['cached'] for row in repeated['records']))
            receipt = next(row for row in first['records'] if row['task_ref'] == 'workbench')
            path = Path(receipt['record'])
            original = path.read_bytes()
            self.items[2]['outcome'] = {'status': 'accepted', 'evidence': ['fixture-result-and-checks'], 'elapsed_seconds': 12}
            self.write()
            code_shadow.record(self.project, self.input, 'verification')
            self.assertTrue(path.read_bytes().startswith(original))
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[-1]['executor']['execution_id'], 'fixture-task')
            self.assertEqual(rows[-1]['purpose'], 'verification')
            boundary.assert_not_called()

    def test_record_rejects_invalid_batch_before_any_write(self):
        valid = dict(task_ref='valid', state='局部任务', reason='直接处理', executor=dict(kind='main', model='current'))
        bad = [dict(valid, task_ref='bad', executor=dict(kind='workbench', model='m', agent_id='a', provider_id='p')),
               dict(valid, task_ref='bad', outcome={'status': 'accepted'}),
               dict(valid, task_ref='bad', reason=''),
               dict(valid, task_ref='bad', executor=dict(kind=['workbench']))]
        for item in bad:
            with self.subTest(item=item):
                self.items = [valid, item]
                self.write()
                with self.assertRaises(ValueError):
                    code_shadow.record(self.project, self.input, 'verification')
                self.assertFalse((self.project / '.codex-adaptive-agents').exists())

    def test_weekly_project_discovery_only_registers_production(self):
        self.items = [dict(task_ref='route', state='局部工作包', reason='直接处理即可',
                           executor=dict(kind='main', model='current'))]
        self.write()
        index = self.home / 'codex-adaptive-agents' / 'route-projects.json'
        code_shadow.record(self.project, self.input, 'verification', self.home)
        self.assertFalse(index.exists())
        for _ in range(2):
            code_shadow.record(self.project, self.input, 'production', self.home)
        self.assertEqual(json.loads(index.read_text())['projects'], [str(self.project)])


if __name__ == '__main__':
    unittest.main()
