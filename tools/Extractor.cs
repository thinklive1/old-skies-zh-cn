using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using System.Collections.Generic;
using AGSUnpacker.Lib.Game;
using AGSUnpacker.Lib.Room;
using AGSUnpacker.Lib.Shared;

public static class Extractor {
  public static void Run(string input, string output) {
    Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
    var entries = new List<object>();
    string asset="game28.dta";
    void Add(string text, string kind, int index, string script="") {
      if (String.IsNullOrWhiteSpace(text)) return;
      // Upstream reads bytes as Latin-1. Actual game encoding is Windows-1252.
      string source=Encoding.GetEncoding(1252).GetString(Encoding.Latin1.GetBytes(text));
      entries.Add(new {source, asset, kind, index, script});
    }
    void Script(AGSScript s, string kind) {
      string name=s.Sections.Length>0?s.Sections.Last().Name:s.Name;
      foreach(var t in s.StringsReferenced) {
        string section=name;
        foreach(var candidate in s.Sections)
          if(candidate.Offset<=t.Offset) section=candidate.Name;
        Add(t.Text,kind,t.Offset,section);
      }
    }
    var g=AGSGameData.ReadFromFile(Path.Combine(input,"game28.dta"));
    for(int i=0;i<g.dialogs.Length;i++)
      for(int j=0;j<g.dialogs[i].options_number;j++) Add(g.dialogs[i].options[j],"dialog-option",j,"dialog"+i);
    Script(g.globalScript,"global-script"); Script(g.dialogScript,"dialog-script");
    foreach(var s in g.scriptModules) Script(s,"module-script");
    for(int i=0;i<g.oldDialogStrings.Count;i++) Add(g.oldDialogStrings[i],"legacy-dialog",i);
    for(int i=0;i<g.labels.Length;i++) Add(g.labels[i].text,"gui-label",i);
    for(int i=0;i<g.buttons.Length;i++) Add(g.buttons[i].text,"gui-button",i);
    for(int i=0;i<g.listboxes.Length;i++) for(int j=0;j<g.listboxes[i].items.Length;j++) Add(g.listboxes[i].items[j],"gui-list",j,"listbox"+i);
    for(int i=0;i<g.characters.Length;i++) Add(g.characters[i].name,"character",i);
    for(int i=0;i<g.inventoryItems.Length;i++) Add(g.inventoryItems[i].name,"inventory",i);
    for(int i=0;i<g.globalMessages.Length;i++) if(g.setup.global_messages[i]!=0) Add(g.globalMessages[i],"global-message",i);
    for(int i=0;i<g.dictionary.words.Length;i++) Add(g.dictionary.words[i].text,"parser-dictionary",i);
    foreach(string file in Directory.GetFiles(input,"room*.crm").OrderBy(p=>Int32.Parse(Path.GetFileNameWithoutExtension(p).Substring(4)))) {
      asset=Path.GetFileName(file); var r=new AGSRoom(Path.GetFileNameWithoutExtension(file)); r.ReadFromFileDeprecated(file);
      for(int i=0;i<r.Markup.Hotspots.Length;i++) Add(r.Markup.Hotspots[i].Name,"hotspot",i);
      for(int i=0;i<r.Markup.Objects.Length;i++) Add(r.Markup.Objects[i].Name,"object",i);
      for(int i=0;i<r.Messages.Length;i++) Add(r.Messages[i].Text,"room-message",i);
      Script(r.Script.SCOM3,"room-script");
      Console.WriteLine(asset+" OK");
    }
    var meta=new { game_uid=g.setup.unique_id, game_name=g.setup.name, format_version=g.Version,
      engine=g.VersionEngine, game_encoding=g.setup.options[AGSGameData.EncodingOption],
      fonts=g.fonts, font_outline_thickness=g.font_outlines_thickness, font_outline_style=g.font_outlines_style,
      room_names=g.roomsDebugInfo.Select(r=>new {r.id,r.name}), entries };
    File.WriteAllText(output,JsonSerializer.Serialize(meta,new JsonSerializerOptions {WriteIndented=true}),new UTF8Encoding(false));
    Console.WriteLine("Extracted occurrences: "+entries.Count);
  }
}
