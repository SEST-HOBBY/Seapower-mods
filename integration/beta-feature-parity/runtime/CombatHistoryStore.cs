using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Sest.RuntimeFixes;

internal sealed class CombatHistoryStore
{
	private const string Header = "SEST-COMBAT-HISTORY-1";

	private readonly string path;

	private readonly Dictionary<string, CombatGameRecord> records = new Dictionary<string, CombatGameRecord>(StringComparer.Ordinal);

	internal bool ReadOnly;

	internal List<CombatGameRecord> Games => records.Values.OrderByDescending((CombatGameRecord r) => r.EndedUtc).ThenBy((CombatGameRecord r) => r.Id, StringComparer.Ordinal).ToList();

	internal CombatHistoryStore(string file)
	{
		path = file;
		if (!File.Exists(path))
		{
			return;
		}
		try
		{
			if (new FileInfo(path).Length > 64000000)
			{
				throw new InvalidDataException("history too large");
			}
			string[] array = File.ReadAllLines(path, Encoding.UTF8);
			if (array.Length == 0 || array[0] != "SEST-COMBAT-HISTORY-1")
			{
				throw new InvalidDataException("unknown history format");
			}
			foreach (string item in array.Skip(1))
			{
				CombatGameRecord combatGameRecord = CombatGameRecord.Decode(item);
				if (combatGameRecord == null || records.ContainsKey(combatGameRecord.Id))
				{
					throw new InvalidDataException("invalid or duplicate history entry");
				}
				records.Add(combatGameRecord.Id, combatGameRecord);
			}
		}
		catch (Exception error)
		{
			ReadOnly = true;
			Api.LogFailure("combat history is read-only; existing file preserved", error);
		}
	}

	internal void Put(CombatGameRecord record)
	{
		if (ReadOnly || record == null)
		{
			return;
		}
		CombatGameRecord combatGameRecord = CombatGameRecord.Decode(record.Encode());
		if (combatGameRecord == null)
		{
			throw new InvalidDataException("invalid combat history record");
		}
		records[record.Id] = combatGameRecord;
		string directoryName = Path.GetDirectoryName(path);
		if (!string.IsNullOrEmpty(directoryName))
		{
			Directory.CreateDirectory(directoryName);
		}
		string sourceFileName = path + "." + Guid.NewGuid().ToString("N") + ".tmp";
		try
		{
			File.WriteAllLines(sourceFileName, new string[1] { "SEST-COMBAT-HISTORY-1" }.Concat(Games.Select((CombatGameRecord r) => r.Encode())), new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
			if (File.Exists(path))
			{
				File.Replace(sourceFileName, path, null);
			}
			else
			{
				File.Move(sourceFileName, path);
			}
		}
		finally
		{
			if (File.Exists(sourceFileName))
			{
				File.Delete(sourceFileName);
			}
		}
	}
}
