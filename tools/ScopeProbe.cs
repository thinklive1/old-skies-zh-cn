// Read-only scope evidence using the same pinned AGSUnpacker as Extractor.cs.
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Collections.Generic;
using AGSUnpacker.Lib.Game;
using AGSUnpacker.Lib.Shared;
using AGSUnpacker.Lib.Shared.Script.Deprecated;

class ScopeProbe {
  static void Main(string[] args) {
    try { Run(args); }
    catch(Exception error) { Console.Error.WriteLine(error); Environment.Exit(1); }
  }
  static void Run(string[] args) {
    Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
    string Text(string value) => Encoding.GetEncoding(1252).GetString(Encoding.Latin1.GetBytes(value));
    var scripts = new List<object>();
    void Add(AGSScript s, string asset, string kind) {
      scripts.Add(new { asset, kind, s.Name, s.Code, s.Imports, s.Exports, s.Sections, s.Fixups,
        strings = s.StringsReferenced.Select(r => new { source=Text(r.Text), index=r.Offset }) });
    }
    var game = AGSGameData.ReadFromFile(Path.Combine(args[0], "game28.dta"));
    Add(game.globalScript, "game28.dta", "global-script");
    Add(game.dialogScript, "game28.dta", "dialog-script");
    foreach(var s in game.scriptModules) Add(s, "game28.dta", "module-script");
    foreach(string file in Directory.GetFiles(args[0], "room*.crm").OrderBy(p => Int32.Parse(Path.GetFileNameWithoutExtension(p).Substring(4)))) {
      // Read only the embedded SCOM payload: avoid decoding room backgrounds
      // through System.Drawing, which is unnecessary for a scope audit.
      byte[] bytes=File.ReadAllBytes(file);
      bool found=false;
      for(int offset=0; offset+20<=bytes.Length; ++offset) {
        if(bytes[offset]!=83 || bytes[offset+1]!=67 || bytes[offset+2]!=79 || bytes[offset+3]!=77) continue;
        int version=BitConverter.ToInt32(bytes,offset+4), globals=BitConverter.ToInt32(bytes,offset+8),
            code=BitConverter.ToInt32(bytes,offset+12), strings=BitConverter.ToInt32(bytes,offset+16);
        if(version<83 || version>100 || globals<0 || code<0 || strings<0 ||
           (long)offset+20+globals+(long)code*4+strings>bytes.Length) continue;
        using var stream=new MemoryStream(bytes,false);
        stream.Position=offset;
        using var reader=new BinaryReader(stream,Encoding.Latin1);
        var script=new AGSScript();script.ReadFromStream(reader);
        if(BitConverter.ToUInt32(bytes,(int)stream.Position-4)!=0xBEEFCAFE) throw new Exception("SCOM trailer mismatch");
        Add(script,Path.GetFileName(file),"room-script");found=true;break;
      }
      if(!found) throw new Exception("No bounded SCOM script in "+Path.GetFileName(file));
    }
    var data = new { game_uid=game.setup.unique_id, rooms=game.roomsDebugInfo,
      dialogs=game.dialogs.Select((d,i) => new { id=i, d.topic_flags,
        options=Enumerable.Range(0,d.options_number).Select(j => new { index=j, source=Text(d.options[j]), flag=d.flags[j] }) }),
      guis=game.guis, labels=game.labels, buttons=game.buttons,
      // AGSGUIListBox hides the base control flags with its own list flags.
      // Record both explicitly so translation/visibility evidence is accurate.
      listboxes=game.listboxes.Select((l,i) => new { index=i, l.name,
        control_flags=((AGSGUIObject)l).flags, listbox_flags=l.flags,
        l.x, l.y, l.width, l.height, l.z_order, l.events,
        l.font, l.items }), scripts,
      instructions=AGSVirtualMachine.Instructions.Select(i => new { opcode=(int)i.Opcode,
        name=i.Mnemonic, arguments=i.ArgumentsCount }) };
    File.WriteAllText(args[1], JsonSerializer.Serialize(data, new JsonSerializerOptions { IncludeFields=true }), new UTF8Encoding(false));
    Console.WriteLine("Scope metadata written; no original asset modified");
  }
}
