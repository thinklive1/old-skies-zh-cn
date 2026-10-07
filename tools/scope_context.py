"""Read instruction context for exact strings; never infer scope from spelling."""
import argparse, bisect
from catalog import read_json


def instructions(script, table):
    code=script['Code'];fixups={f['Offset']:f['Type'] for f in script['Fixups']}
    strings={r['index']:r['source'] for r in script['strings']}
    exports={e['Pointer']:e['Name'] for e in script['Exports'] if e['Type']==1}
    result=[];pc=0
    while pc<len(code):
        opcode=code[pc]&0xffffff
        if opcode not in table:raise ValueError(f'Unknown opcode {opcode} at {script["asset"]}:{pc}')
        item=table[opcode];end=pc+1+item['arguments']
        if end>len(code):raise ValueError('Truncated instruction')
        args=[]
        for pos in range(pc+1,end):
            value=code[pos];kind=fixups.get(pos,0)
            if kind==3:value=repr(strings[pos])
            elif kind==4:value='IMPORT:'+script['Imports'][value]
            elif kind==2:value='FUNCTION:'+exports.get(value,str(value))
            elif kind==1:value='GLOBAL@'+str(value)
            args.append(value)
        result.append(dict(pc=pc,end=end,name=item['name'],args=args))
        pc=end
    return result


def context(metadata, sources, radius=18):
    data=read_json(metadata);table={i['opcode']:i for i in data['instructions']}
    for script in data['scripts']:
        selected=[r for r in script['strings'] if r['source'] in sources]
        if not selected:continue
        code=instructions(script,table);positions=[i['pc'] for i in code]
        for row in selected:
            index=bisect.bisect_right(positions,row['index'])-1
            sections=[s for s in script['Sections'] if s['Offset']<=row['index']]
            print('\nSOURCE',repr(row['source']),script['asset'],sections[-1]['Name'] if sections else script['Name'],row['index'])
            for instruction in code[max(0,index-radius):index+radius+1]:
                print(instruction['pc'],instruction['name'],*instruction['args'])


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('metadata');parser.add_argument('source',nargs='+');parser.add_argument('--radius',type=int,default=18)
    args=parser.parse_args();context(args.metadata,set(args.source),args.radius)
