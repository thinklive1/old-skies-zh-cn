"""Append a UTF-8, pixel-width wrapper without changing existing string references.

Only used with a selected translation. The English path resumes the original
code. Managed arguments and temporary strings have explicit cleanup paths.
"""
from scom_runtime import parse, serialize


def patch(blob, table):
    original = parse(blob)
    if original['end'] != len(blob) or original['sections'] != [dict(name='Scrollers.asc', offset=0)]:
        raise ValueError('Unexpected Scrollers module')
    if {e['name']:e['pointer'] for e in original['exports']} != {'MakeScrollList$2':0,'MakeEmail$4':2193}:
        raise ValueError('Unexpected export layout')
    op = {i['name']:i['opcode'] for i in table}
    code=original['code'].copy(); imports=original['imports'].copy(); fixups=original['fixups'].copy()
    extra=[]; labels={}; branches=[]; stack=0
    if imports[0]: raise ValueError('Already patched module')
    for name in ['GetTranslation','GetTextWidth','IsTranslationAvailable']:
        imports[imports.index('')]=name
    def emit(name,*args):
        nonlocal stack
        if name=='movlit' and isinstance(args[1],str):
            extra.append((4,len(code)+2));args=(args[0],imports.index(args[1]))
        code.extend([op[name],*args])
        if name=='push': stack+=4
        elif name=='pop':stack-=4
        elif name=='add' and args[0]==1:stack+=args[1]
        elif name=='sub' and args[0]==1:stack-=args[1]
    def mark(name): labels[name]=len(code)
    def jump(name,kind='jmp'):
        branches.append((len(code)+1,name));emit(kind,0)
    def native(name,n):
        emit('setfuncargs',n);emit('movlit',3,name);emit('callext',3)
        if n:emit('subreal',n)
    def arg(offset,ptr=True):
        emit('loadspoffs',offset+stack);emit('memreadptr' if ptr else 'memread',3)
    def local(index,ptr=True):
        emit('loadspoffs',stack-4*index);emit('memreadptr' if ptr else 'memread',3)
    def store(index,ptr=True):
        emit('loadspoffs',stack-4*index);emit('memwriteptr' if ptr else 'memwrite',3)
    def allocate(ptr):
        emit('movreg',1,2);emit('meminitptr' if ptr else 'memwrite',3);emit('add',1,4)
    def member_arg(name,object_get,argument_get=None):
        emit('push',6)
        if argument_get:argument_get();emit('pushreal',3)
        object_get();emit('thisptr',3);native(name,1 if argument_get else 0);emit('pop',6)
    def flush():member_arg('ListBox::AddItem^1',lambda:arg(8),lambda:local(0))
    def empty():member_arg('String::Truncate^1',lambda:arg(12),lambda:emit('movlit',3,0))
    def increment():local(2,False);emit('add',3,1);store(2,False)
    def translate():emit('pushreal',3);native('GetTranslation',1);emit('newstr',3)
    def literal(text):
        pool=original['strings']; needle=text.encode('cp1252')+b'\0';position=pool.find(needle)
        while position>0 and pool[position-1]!=0:position=pool.find(needle,position+1)
        if position<0 or (position and pool[position-1]!=0):raise ValueError('Missing original literal '+text)
        extra.append((3,len(code)+2));emit('movlit',3,position)
    def direct_wrap(list_get,text_get):
        # Internal script arguments use the VM stack, not the native argument stack.
        text_get();emit('push',3);list_get();emit('push',3)
        extra.append((2,len(code)+2));emit('movlit',3,labels['wrap']);emit('call',3);emit('sub',1,8)
    # Internal wrapper arguments: ListBox at +8, managed text at +12.
    mark('wrap');emit('baseptr',len(code))
    for offset in [8,12]:arg(offset,False);emit('loadspoffs',offset);emit('meminitptr',3)
    empty();allocate(True)          # line
    local(0);allocate(True)         # candidate
    emit('movlit',3,0);allocate(False)  # index
    member_arg('String::get_Length',lambda:arg(12));allocate(False)
    emit('movlit',3,0);allocate(False)  # codepoint
    mark('loop');local(2,False);emit('push',3);local(3,False);emit('pop',4)
    emit('le',4,3);emit('movreg',4,3);jump('finish','jz')
    member_arg('String::geti_Chars',lambda:arg(12),lambda:local(2,False));store(4,False)
    emit('push',3);emit('movlit',3,91);emit('pop',4);emit('eq',4,3);emit('movreg',4,3);jump('normal','jz')
    flush();empty();store(0);increment();jump('loop')
    mark('normal')
    member_arg('String::AppendChar^1',lambda:local(0),lambda:local(4,False));store(1)
    emit('movlit',3,0);emit('pushreal',3);local(1);emit('pushreal',3);native('GetTextWidth',2)
    emit('push',3);emit('movlit',3,260);emit('pop',4);emit('gr',4,3);emit('movreg',4,3);jump('accept','jz')
    member_arg('String::get_Length',lambda:local(0));jump('accept','jz')
    flush();empty();store(0)
    member_arg('String::AppendChar^1',lambda:local(0),lambda:local(4,False));store(1)
    mark('accept');local(1);store(0);increment();jump('loop')
    mark('finish');flush()
    for offset in [0,1]:emit('loadspoffs',stack-4*offset);emit('memzeroptrnd')
    emit('sub',1,20)
    for offset in [8,12]:emit('loadspoffs',offset);emit('memzeroptrnd')
    emit('movlit',3,0);emit('ret')
    if stack:raise ValueError('Wrapper stack imbalance')
    detours=[]
    for hook,line,mode in [(10,9,'news'),(2221,99,'mail')]:
        if code[hook:hook+2]!=[op['sourceline'],line] or any(hook<=pos<hook+2 for _,pos in fixups):raise ValueError('Unsafe entry hook')
        helper=len(code);code[hook:hook+2]=[op['jmp'],helper-hook-2]
        # No active translation: continue byte-for-byte original English behavior.
        native('IsTranslationAvailable',0);jump(mode+'-original','jz')
        if mode=='news':
            for field in ['ScrollText1','ScrollText2','ScrollText3','ScrollText4']:
                emit('movlit',2,field);emit('memreadptr',3);translate();emit('movlit',2,field);emit('memwriteptr',3)
            for field in ['ScrollText2','ScrollText3','ScrollText4']:
                member_arg('String::Append^1',lambda:(emit('movlit',2,'ScrollText1'),emit('memreadptr',3)),
                           lambda field=field:(emit('movlit',2,field),emit('memreadptr',3)))
                emit('movlit',2,'ScrollText1');emit('memwriteptr',3)
            member_arg('ListBox::Clear^0',lambda:arg(8))
            direct_wrap(lambda:arg(8),lambda:(emit('movlit',2,'ScrollText1'),emit('memreadptr',3)))
            emit('loadspoffs',8);emit('memzeroptrnd')
        else:
            for offset in [8,12,16,20]:arg(offset);translate();emit('loadspoffs',offset);emit('memwriteptr',3)
            def mail_list():emit('movlit',2,'ListBoxEmailMessage1');emit('movreg',2,3)
            def add_literal(text):member_arg('ListBox::AddItem^1',mail_list,lambda:(literal(text),translate()))
            member_arg('ListBox::Clear^0',mail_list)
            for text,offset in [('FROM:',8),('RECEIVED:',12),('SUBJECT:',16)]:
                add_literal(text)
                direct_wrap(mail_list,lambda offset=offset:arg(offset))
            for text in ['--------------------',' ',' ']:add_literal(text)
            direct_wrap(mail_list,lambda:arg(20))
            for _ in range(3):add_literal(' ')
            for offset in [8,12,16,20]:emit('loadspoffs',offset);emit('memzeroptrnd')
        emit('movlit',3,0);emit('ret')
        mark(mode+'-original');emit('sourceline',line);emit('jmp',hook+2-(len(code)+2))
        if stack:raise ValueError('Entry helper stack imbalance')
        detours.append(dict(hook=hook,helper=helper,mode=mode))
    for pos,name in branches:code[pos]=labels[name]-(pos+1)
    patched=serialize({**original,'code':code,'imports':imports,'fixups':fixups+extra}); reread=parse(patched)
    if any(reread[k]!=original[k] for k in ['strings','globals','tail']):raise ValueError('Changed original structure')
    changed=[i for i,(a,b) in enumerate(zip(original['code'],code)) if a!=b]
    if changed!=[10,11,2221,2222]:raise ValueError('Changed unexpected code cells')
    return patched,dict(detours=detours,original_code_cells=len(original['code']),added_code_cells=len(code)-len(original['code']),
      changed_code_cells=changed,added_imports=['GetTranslation','GetTextWidth','IsTranslationAvailable'],
      added_fixups=[list(pair) for pair in extra],wrapping='UTF-8 codepoints, actual font-0 width <=260px, explicit [ line breaks',english_path='original code without an active translation')
