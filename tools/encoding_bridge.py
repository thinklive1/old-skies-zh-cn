"""Select TRA entries without changing editorial progress.

An AGS UTF-8 translation changes the display encoding globally. A missing
translation otherwise falls back to the original CP1252 bytes. Keep accented
source text readable during development and keep commentary text in English.
"""

from context_data import aliases


def select_pairs(rows, development=False):
    accepted = {'reviewed', 'preserve'}
    if development:
        accepted.add('translated')
    rows = list(rows)
    split = aliases()
    source_keys = {row['source'] for row in rows}
    if any(entry['runtime_key'] in source_keys for entry in split.values()):
        raise ValueError('Runtime alias collides with a source key')
    pairs = []
    bridges = []
    for row in rows:
        if row['id'] in split:
            entry = split[row['id']]
            if row['source'] != entry['source']:
                raise ValueError('Runtime alias source mismatch')
            # The original key is commentary; the alias is story only. An
            # unfinished story uses English until its editorial row is ready.
            pairs.append((entry['runtime_key'], row['target'] if row['status'] in accepted else row['source']))
            pairs.append((row['source'], row['source']))
            bridges.append(row['id'])
        elif row['status'] in accepted:
            pairs.append((row['source'], row['target']))
        elif (row['status'] == 'excluded' and row['reason'] == '开发者解说沿用英文') or (
            row['status'] != 'excluded' and not row['source'].isascii()
        ):
            pairs.append((row['source'], row['source']))
            bridges.append(row['id'])
    return pairs, bridges
