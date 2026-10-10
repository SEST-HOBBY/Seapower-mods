// SEST Menu Background - plays the SEST film behind Sea Power's main menu.
//
// The main menu's film is a VideoClip inside the game's Unity data
// (sharedassets1.resource), not a file a mod can stand in for. Anchor Chain
// (Workshop 3380210757, which SEST's SETUP installs) loads every DLL in every
// mod folder the game knows and starts each class marked [ACPlugin] that
// implements IAnchorChainMod - the SEST pack's plugins/ folder included. This
// one finds the Unity VideoPlayer that loops the menu's clip and points it at
// plugins/sest_menu.mp4 instead. No game code is patched and no game type is
// referenced, only Unity's own VideoPlayer.
//
// What it will and will not swap:
//   - only a player already set to loop and playing a clip from the game's
//     data. A one-shot film the game may wait on to finish (an intro) is
//     never looped and never touched; the mission browser's films (the video
//     tutorials, the SEST Briefing Room) play from a file and are skipped;
//   - the first such clip seen is taken as the menu's, and after that only
//     that clip is swapped (the menu is rebuilt after every mission).
//     sest_menu.ini can name the clip instead, or turn the plugin off;
//   - if Unity cannot play the SEST film, the game's own clip is put back.
// Every player it sees is written to Player.log with "[SEST Menu]", which
// tools/capture-context.ps1 brings into the repo.
//
// Built by build_plugin.py against Unity's public API and Anchor Chain's
// two public types (stubs/AnchorChain.cs).
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using AnchorChain;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.Video;

namespace Sest.MenuBackground
{
    // Anchor Chain creates this with Activator.CreateInstance, which a Unity
    // component cannot be, so the entry point builds the component itself on
    // a GameObject that survives scene changes.
    [ACPlugin("io.github.sest-hobby.menu-background", "SEST Menu Background", "1.0.0")]
    public class MenuBackgroundMod : IAnchorChainMod
    {
        public void TriggerEntryPoint()
        {
            var host = new GameObject("SEST Menu Background");
            UnityEngine.Object.DontDestroyOnLoad(host);
            host.AddComponent<MenuFilmSwapper>();
        }
    }

    public class MenuFilmSwapper : MonoBehaviour
    {
        const string Tag = "[SEST Menu] ";
        const string IniName = "sest_menu.ini";
        const string SestWorkshopId = "3812461539";

        readonly HashSet<int> seen = new HashSet<int>();
        readonly Dictionary<int, VideoClip> original = new Dictionary<int, VideoClip>();
        string film;          // the SEST film's full path; null when off or missing
        string menuClip;      // the menu's clip name, from the ini or the first looping clip seen
        float scanUntil, nextScan;

        void Awake()
        {
            try { Configure(); }
            catch (Exception e) { film = null; Debug.LogWarning(Tag + "not started: " + e.Message); }
            SceneManager.sceneLoaded += OnSceneLoaded;
            // The game can take minutes to load a large collection before the
            // menu shows; look for ten, then for half a minute after each scene.
            scanUntil = Time.realtimeSinceStartup + 600f;
        }

        void OnSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            scanUntil = Mathf.Max(scanUntil, Time.realtimeSinceStartup + 30f);
        }

        void Update()
        {
            float now = Time.realtimeSinceStartup;
            if (film == null || now > scanUntil || now < nextScan) return;
            nextScan = now + 0.5f;
            try { Scan(); }
            catch (Exception e) { film = null; Debug.LogWarning(Tag + "stopped: " + e.Message); }
        }

        void Scan()
        {
            VideoPlayer[] players = UnityEngine.Object.FindObjectsByType<VideoPlayer>(
                FindObjectsInactive.Include, FindObjectsSortMode.None);
            foreach (VideoPlayer vp in players)
            {
                if (vp == null || !seen.Add(vp.GetInstanceID())) continue;
                string clip = vp.clip != null ? vp.clip.name : "";
                Debug.Log(Tag + "video player '" + PathOf(vp.transform) + "' in scene '" + vp.gameObject.scene.name
                          + "': source=" + vp.source + " clip='" + clip + "' url='" + vp.url + "' render="
                          + vp.renderMode + " loop=" + vp.isLooping + " playing=" + vp.isPlaying
                          + " audio=" + vp.audioOutputMode);
                if (vp.source != VideoSource.VideoClip || vp.clip == null || !vp.isLooping) continue;
                if (string.IsNullOrEmpty(menuClip))
                {
                    menuClip = clip;
                    Debug.Log(Tag + "taking the looping clip '" + clip + "' as the main menu film");
                }
                if (clip == menuClip) Swap(vp);
            }
        }

        void Swap(VideoPlayer vp)
        {
            bool play = vp.isPlaying || vp.playOnAwake;
            original[vp.GetInstanceID()] = vp.clip;
            vp.Stop();
            vp.source = VideoSource.Url;
            vp.url = film;
            vp.isLooping = true;
            vp.errorReceived += OnError;
            if (play) vp.Play();
            Debug.Log(Tag + "menu film now " + film);
        }

        void OnError(VideoPlayer vp, string message)
        {
            vp.errorReceived -= OnError;
            VideoClip clip;
            if (!original.TryGetValue(vp.GetInstanceID(), out clip)) return;
            Debug.LogWarning(Tag + "the SEST film did not play (" + message + "); the game's own film is back");
            vp.Stop();
            vp.source = VideoSource.VideoClip;
            vp.clip = clip;
            vp.Play();
        }

        void Configure()
        {
            string dir = PluginDir();
            if (dir == null) throw new Exception(IniName + " not found beside the plugin, in StreamingAssets or the Workshop folder");
            var ini = ReadIni(Path.Combine(dir, IniName));
            string v;
            if (ini.TryGetValue("Enabled", out v) && v.Trim() == "0")
            {
                Debug.Log(Tag + "off (Enabled=0 in " + IniName + ")");
                return;
            }
            string name = ini.TryGetValue("Film", out v) && v.Trim().Length > 0 ? v.Trim() : "sest_menu.mp4";
            string path = Path.Combine(dir, name);
            if (!File.Exists(path)) throw new Exception("film not found: " + path);
            if (ini.TryGetValue("ClipName", out v) && v.Trim().Length > 0) menuClip = v.Trim();
            film = path;
            Debug.Log(Tag + "ready: " + film + (menuClip != null ? " for clip '" + menuClip + "'" : ""));
        }

        // The folder holding sest_menu.ini: beside this DLL when the loader
        // reports its path, else the pack's copy in StreamingAssets, else its
        // Workshop copy (any subscribed item carrying plugins/sest_menu.ini).
        static string PluginDir()
        {
            var tries = new List<string>();
            try
            {
                string loc = Assembly.GetExecutingAssembly().Location;
                if (!string.IsNullOrEmpty(loc)) tries.Add(Path.GetDirectoryName(loc));
            }
            catch (Exception) { }
            tries.Add(Path.Combine(Path.Combine(Application.streamingAssetsPath, "SEST_Integration"), "plugins"));
            try
            {
                DirectoryInfo steamapps = new DirectoryInfo(Application.dataPath).Parent.Parent.Parent;
                string content = Path.Combine(Path.Combine(Path.Combine(steamapps.FullName, "workshop"), "content"), "1286220");
                tries.Add(Path.Combine(Path.Combine(content, SestWorkshopId), "plugins"));
                if (Directory.Exists(content))
                    foreach (string d in Directory.GetDirectories(content)) tries.Add(Path.Combine(d, "plugins"));
            }
            catch (Exception) { }
            foreach (string d in tries)
                if (File.Exists(Path.Combine(d, IniName))) return d;
            return null;
        }

        static Dictionary<string, string> ReadIni(string path)
        {
            var d = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (string raw in File.ReadAllLines(path))
            {
                string line = raw.Trim();
                if (line.Length == 0 || line[0] == ';' || line[0] == '#' || line[0] == '[') continue;
                int eq = line.IndexOf('=');
                if (eq > 0) d[line.Substring(0, eq).Trim()] = line.Substring(eq + 1);
            }
            return d;
        }

        static string PathOf(Transform t)
        {
            string p = t.name;
            for (Transform u = t.parent; u != null; u = u.parent) p = u.name + "/" + p;
            return p;
        }
    }
}
