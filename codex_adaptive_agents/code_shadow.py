"""Execution records and coding-only shadow observations through the local Laya monitor."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys

from .install import EFFORTS, RESOURCE
from .platform import atomic, clean_env, encode, file_lock, loads, read, run

SCENARIO = 'coding-effort-shadow'
VERSION = 'code-shadow-v1'
ROUTE_VERSION = 'code-route-v1'


def record(project, input_path, purpose, home=None):
    """Append execution evidence for all routes, without starting a model or task."""
    if purpose not in ('production', 'verification') or not project.is_dir():
        raise ValueError('code-record requires an existing project and production|verification purpose')
    raw = read(input_path)
    if raw is None or len(raw) > 128 * 1024:
        raise ValueError('code-record requires a JSONL file of at most 128 KiB')
    items, seen = [], set()
    for line in raw.decode('utf-8').splitlines():
        if not line.strip():
            continue
        item = loads(line)
        required = {'task_ref', 'state', 'executor', 'reason'}
        if (not isinstance(item, dict) or not required <= set(item) or
                set(item) - required - {'alternatives', 'evidence', 'outcome'}):
            raise ValueError('code-record requires task_ref, state, executor and reason')
        ref = item['task_ref']
        if not isinstance(ref, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', ref) or ref in seen:
            raise ValueError('task_ref must be a unique stable identifier in this batch')
        if any(not isinstance(item[k], str) or not item[k].strip() for k in ('state', 'reason')):
            raise ValueError('state and selection reason must be nonempty')
        executor = item['executor']
        fields = {'main': {'kind', 'model'},
                  'native': {'kind', 'model', 'execution_id'},
                  'luna': {'kind', 'model', 'role', 'execution_id'},
                  'workbench': {'kind', 'model', 'agent_id', 'provider_id', 'execution_id'}}
        if (not isinstance(executor, dict) or not isinstance(executor.get('kind'), str) or executor.get('kind') not in fields or
                set(executor) != fields[executor['kind']] or
                any(not isinstance(v, str) or not v.strip() or len(v) > 512 for v in executor.values())):
            raise ValueError('executor requires the actual model and route-specific execution identifiers')
        if executor['kind'] == 'luna' and (executor['model'] != 'gpt-6-luna' or
                executor['role'] not in ['adaptive_luna_' + e for e in EFFORTS]):
            raise ValueError('Luna executor must match an installed role and model')
        for key in ('alternatives', 'evidence'):
            if key in item and (not isinstance(item[key], list) or
                    any(not isinstance(v, str) or not v.strip() for v in item[key])):
                raise ValueError(key + ' requires a list of nonempty strings')
        outcome = item.get('outcome')
        if outcome is not None:
            if (not isinstance(outcome, dict) or outcome.get('status') not in
                    ('accepted', 'needs_rework', 'failed', 'cancelled', 'unknown')):
                raise ValueError('outcome requires an explicit status')
            evidence = outcome.get('evidence', [])
            if (not isinstance(evidence, list) or
                    any(not isinstance(v, str) or not v.strip() for v in evidence) or
                    (outcome['status'] != 'unknown' and not evidence)):
                raise ValueError('a known outcome requires evidence')
        items.append(item)
        seen.add(ref)
    if not 1 <= len(items) <= 50:
        raise ValueError('code-record requires 1 to 50 work packages')
    results = []
    for item in sorted(items, key=lambda value: value['task_ref']):
        data = dict(scenario_version=ROUTE_VERSION, purpose=purpose, project=str(project), **item)
        event_id = hashlib.sha256(encode(data)).hexdigest()
        task_hash = hashlib.sha256(item['task_ref'].encode('utf-8')).hexdigest()
        path = project / '.codex-adaptive-agents' / 'routes' / task_hash / 'events.jsonl'
        with file_lock(path.with_name('lock')):
            previous = read(path) or b''
            # ponytail: scan one task's small event log; use indexed storage if task histories grow large.
            events = [loads(line) for line in previous.splitlines() if line.strip()]
            cached = any(event.get('event_id') == event_id for event in events)
            if not cached:
                event = dict(event_id=event_id, at=datetime.now(timezone.utc).isoformat(), **data)
                row = json.dumps(event, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')
                atomic(path, previous + (b'\n' if previous and not previous.endswith(b'\n') else b'') + row + b'\n')
        results.append(dict(task_ref=item['task_ref'], event_id=event_id, record=str(path), cached=cached))
    index = None
    if home is not None and purpose == 'production':
        index = home / RESOURCE / 'route-projects.json'
        with file_lock(index.with_name('route-projects.lock')):
            saved = read(index)
            value = loads(saved) if saved is not None else {'version': 1, 'projects': []}
            if (not isinstance(value, dict) or value.get('version') != 1 or
                    not isinstance(value.get('projects'), list) or
                    any(not isinstance(p, str) or not Path(p).is_absolute() for p in value['projects'])):
                raise ValueError('invalid route project index; task records were saved, inspect the index')
            if str(project) not in value['projects']:
                value['projects'] = sorted(set(value['projects']) | {str(project)})
                atomic(index, encode(value))
    return dict(status='CODE_RECORDED', scenario_version=ROUTE_VERSION, records=results,
                project_index=str(index) if index is not None else None,
                execution_started=False, decision_changed=False)


def requests(path):
    raw = read(path)
    if raw is None or len(raw) > 128 * 1024:
        raise ValueError('code-shadow requires a JSONL file of at most 128 KiB')
    items = []
    seen = set()
    for line in raw.decode('utf-8').splitlines():
        if not line.strip():
            continue
        item = loads(line)
        if not isinstance(item, dict) or set(item) != {'task_ref', 'state', 'efforts', 'actual_role'}:
            raise ValueError('each coding item requires task_ref, state, efforts and actual_role')
        ref = item['task_ref']
        if not isinstance(ref, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', ref) or ref in seen:
            raise ValueError('task_ref must be a unique stable identifier in this batch')
        if not isinstance(item['state'], str) or not item['state'].strip():
            raise ValueError('state must contain the frozen coding work package')
        efforts = item['efforts']
        if (not isinstance(efforts, list) or not 2 <= len(efforts) <= 5 or
                any(not isinstance(e, str) or e not in EFFORTS for e in efforts) or
                len(set(efforts)) != len(efforts)):
            raise ValueError('efforts requires 2 to 5 distinct supported Luna efforts')
        if item['actual_role'] not in ['adaptive_luna_' + e for e in efforts]:
            raise ValueError('actual_role must match an effort in the candidate snapshot')
        item['efforts'] = [e for e in EFFORTS if e in efforts]
        items.append(item)
        seen.add(ref)
    if not items or len(items) > 50:
        raise ValueError('code-shadow requires 1 to 50 work packages')
    return sorted(items, key=lambda item: item['task_ref'])


def observe(home, project, input_path, purpose):
    if purpose not in ('production', 'verification'):
        raise ValueError('code-shadow purpose must be production or verification')
    if not project.is_dir():
        raise ValueError('code-shadow project directory must exist')
    items = requests(input_path)
    model_inputs = []
    for item in items:
        model_inputs.append(dict(id=item['task_ref'], state=item['state'], questions={
            'readiness': dict(type='choice', instructions='这些代码任务材料是否足以判断所需推理程度？',
                criteria={'sufficient': '目标、改动边界和验收依据足够明确',
                          'insufficient': '存在会显著改变实施方案的材料或条件缺口'}),
            'effort': dict(type='score',
                instructions='仅根据代码工作包推荐推理档位。考虑目标清晰度、材料冲突、跨模块依赖和可验证性；不要仅因 coding 标签、篇幅或文件数量升档。',
                criteria=item['efforts'])}))
    # ponytail: cache identical batches only; add per-task reuse if overlapping batches become common.
    key = hashlib.sha256(encode(model_inputs)).hexdigest()
    folder = project / '.codex-adaptive-agents' / 'shadow' / key
    base = dict(mode='shadow', execution_authorized=False, decision_changed=False,
                scenario=SCENARIO, snapshot=str(folder / 'snapshot.json'),
                receipt=str(folder / 'receipt.json'))
    monitor = home / 'laya-monitor' / 'monitor.py'
    if not monitor.is_file():
        return dict(base, status='SHADOW_UNAVAILABLE', error='local laya-monitor is unavailable')
    with file_lock(folder / 'lock'):
        snapshot = dict(version=VERSION, project=str(project), purpose=purpose, items=items)
        previous = read(folder / 'snapshot.json')
        if previous is not None and loads(previous) != snapshot:
            raise ValueError('this frozen batch already has different dispatch metadata; inspect the receipt')
        saved = read(folder / 'result.json')
        if saved is not None:
            return dict(loads(saved), cached=True)
        if previous is not None:
            return dict(base, status='SHADOW_INCOMPLETE',
                        error='prior attempt may have run; inspect receipt before any recovery')
        atomic(folder / 'snapshot.json', encode(snapshot))
        payload = ''.join(json.dumps(value, ensure_ascii=False, allow_nan=False) + '\n'
                          for value in model_inputs).encode('utf-8')
        atomic(folder / 'input.jsonl', payload)
        context = {'version': 1, 'items': [dict(line=i, project=str(project),
            task_ref=item['task_ref'], step='coding-effort-' + hashlib.sha256(encode(model_inputs[i - 1])).hexdigest()[:24],
            scenario_version=VERSION,
            source_paths=[str(folder / 'snapshot.json')],
            baseline_choice=item['actual_role'].removeprefix('adaptive_luna_'),
            candidate_catalog_sha=hashlib.sha256(encode(item['efforts'])).hexdigest(),
            preprocessing_version='frozen-code-work-package-v1') for i, item in enumerate(items, 1)]}
        atomic(folder / 'context.json', encode(context))
        env = clean_env()
        env['LAYA_CALLER'] = 'codex'
        command = [sys.executable, '-B', str(monitor), 'run', 'consult', '--caller', 'codex',
                   '--purpose', purpose, '--scenario', SCENARIO, '--project', str(project),
                   '--input', str(folder / 'input.jsonl'), '--context', str(folder / 'context.json'),
                   '--receipt', str(folder / 'receipt.json')]
        try:
            completed = run(command, env=env, timeout=120)
            atomic(folder / 'stdout.jsonl', completed.stdout)
            atomic(folder / 'stderr.log', completed.stderr)
            responses = [loads(line) for line in completed.stdout.splitlines() if line.strip()]
            valid = len(responses) == len(items) and all(
                r.get('id') == item['task_ref'] and r.get('line') == i and
                r.get('advisory_only') is True and r.get('execution_authorized') is False and
                r.get('tracking', {}).get('captured') is True and
                r['tracking'].get('call_id') and r['tracking'].get('task_key') and
                set(r['tracking'].get('question_ids', {})) == {'readiness', 'effort'}
                for i, (r, item) in enumerate(zip(responses, items), 1))
            result = dict(base, status='SHADOW_RECORDED' if valid and not completed.returncode and
                          all(r.get('ok') is True for r in responses) else 'SHADOW_FAILED',
                          responses=responses, cached=False, observation_recorded=False)
            if valid:
                events = []
                for item, response in zip(items, responses):
                    for name, qid in response['tracking']['question_ids'].items():
                        event = dict(event_id=qid + ':shadow-v1', entity_type='question', entity_id=qid,
                                     reviewer='codex', adoption='not_applicable', decision_changed=False,
                                     reason='旁路判断未参与派发；此记录不评价建议正确性。')
                        if name == 'effort':
                            event['actual_choice'] = item['actual_role'].removeprefix('adaptive_luna_')
                        events.append(event)
                atomic(folder / 'observation.json', encode(events))
                recorded = run([sys.executable, '-B', str(monitor), 'event', '--input',
                                str(folder / 'observation.json')], env=env, timeout=10)
                atomic(folder / 'event.log', recorded.stdout + recorded.stderr)
                result['observation_recorded'] = recorded.returncode == 0
        except (OSError, RuntimeError, ValueError, KeyError, TypeError, AttributeError):
            result = dict(base, status='SHADOW_FAILED', cached=False,
                          error='local inference or tracking failed; inspect private logs and receipt')
        atomic(folder / 'result.json', encode(result))
        return result
