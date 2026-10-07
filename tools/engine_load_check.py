"""Load/parse in an isolated project, exit before game init and save loading."""
from pathlib import Path
import sys,json,importlib.util,hashlib,collections
GAME=Path(r'D:\software\steam\steamapps\common\oath')
PROJECT=Path(__file__).resolve().parents[1]
stage=Path(sys.argv[1]).resolve();report_path=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(GAME));sys.path.insert(0,str(GAME/'lib/py3-windows-x86_64'))
import renpy
original_import=renpy.import_all
def with_check_hook():
    original_import()
    original_load=renpy.script.Script.load_script
    def check_load(self):
        original_load(self)
        errors=[str(x) for x in renpy.parser.parse_errors]
        counts=collections.Counter();invariants=[]
        for node in self.namemap.values():
            kind=type(node).__name__;counts[kind]+=1
            if kind=='If':invariants.append([kind,[str(e) for e,b in node.entries]])
            elif kind=='While':invariants.append([kind,str(node.condition)])
            elif kind=='Jump':invariants.append([kind,str(node.target),bool(node.expression)])
            elif kind=='Call':invariants.append([kind,str(node.label),bool(node.expression)])
            elif kind=='Label':invariants.append([kind,str(node.name)])
            elif kind in ('Say','TranslateSay'):invariants.append([kind,str(node.who),bool(node.interact)])
            elif kind=='Menu':invariants.append([kind,[str(condition) for caption,condition,block in node.items]])
        invariant_data=json.dumps(sorted(invariants,key=repr),ensure_ascii=False,sort_keys=True).encode('utf-8')
        result=dict(success=not errors,game_init_executed=False,save_loading_executed=False,
            parse_errors=errors,loaded_statement_count=len(self.namemap),
            source_loaded=self.loaded_rpy,compiled_script_count=len(self.script_files),
            engine=renpy.version,node_type_counts=dict(counts),
            branch_call_speaker_sha256=hashlib.sha256(invariant_data).hexdigest())
        report_path.parent.mkdir(parents=True,exist_ok=True)
        report_path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in result.items() if k!='parse_errors'},ensure_ascii=False),flush=True)
        if errors:print('\n'.join(errors[:6]),flush=True)
        raise SystemExit(0 if result['success'] else 1)
    renpy.script.Script.load_script=check_load
renpy.import_all=with_check_hook
spec=importlib.util.spec_from_file_location('oath_engine_entry',GAME/'oath.py')
entry=importlib.util.module_from_spec(spec);sys.modules[spec.name]=entry;spec.loader.exec_module(entry)
entry.path_to_common=lambda renpy_base:str(stage/'engine-common')
sys.argv=[str(GAME/'oath.py'),str(stage),'compile','--savedir',str(stage/'isolated-saves'),'--keep-orphan-rpyc']
entry.main()
