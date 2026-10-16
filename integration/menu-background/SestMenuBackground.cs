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
//   - the clip sest_menu.ini names (ClipName=main_menu: the 10 Oct 2026 test
//     showed the menu's player, 'MediaPlayer' in the 'background' scene,
//     playing the clip main_menu with loop off - the game restarts it
//     itself, so a looping-only rule never matched it). Without a name, only
//     a player already set to loop is taken, so a one-shot film the game may
//     wait on to finish (an intro) is never touched;
//   - the mission browser's films (the video tutorials) play from a file
//     and are always skipped;
//   - the menu clip plays its sound straight from the film (audio=Direct),
//     so the menu music may be its sound track: that keeps playing from the
//     game's clip on a second player with no picture;
//   - if the game sets its clip again, the SEST film goes back on; if Unity
//     cannot play the SEST film, the game's own clip is put back.
// Every player it sees is written to Player.log with "[SEST Menu]", which
// tools/capture-context.ps1 brings into the repo.
//
// Since 14 Oct 2026 it also keeps the stock-pictures log (Pictures=1 in the
// ini, on unless set to 0): a bounded record, on lines starting
// "[SEST Pictures]", of every picture the game has loaded and every UI
// element showing one, so a Player.log from the PC can say which texture the
// startup screen, the still between menu pages and the Mod Manager draw and
// what the UI binds each to (docs/workshop-refresh-20261013-review.md,
// section 9). It only reads; PictureLog below says what and when. The film
// swap runs as before with the log on or off. The log has not yet been run
// in the game.
//
// Since 15 Oct 2026 it also puts SEST photographs in place of every other
// picture the game draws as a backdrop (PictureSwap, Backdrops=1 in the ini,
// on unless set to 0). The 15 Oct log showed why a file cannot do it: the
// game pools every ui/backgrounds picture of the base game and of every mod
// and does not let a same-named file stand in for another (it showed the
// stock loading_screen_63 and The Royal Navy's loading_screen_17 though the
// pack ships both names). So the plugin finds each such picture once the game
// has loaded it - a Unity texture named by its file's path - and paints a
// SEST photograph into it, the same texture, so the loading screen, the menu
// backdrop behind the scenario and campaign pages and the Mod Manager show
// SEST's. Campaign and mission title pictures from outside the pack
// (CampaignArt=1) are treated the same way. Unit photos, flags, maps and the
// game's logos are not touched.
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
    [ACPlugin("io.github.sest-hobby.menu-background", "SEST Menu Background", "1.2.1")]
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

        class Swapped
        {
            public VideoPlayer Player, Sound;
            public VideoClip Clip;
            public bool Loop;
            public VideoAudioOutputMode Audio;
        }

        readonly HashSet<int> seen = new HashSet<int>();
        readonly List<Swapped> swapped = new List<Swapped>();
        string film;          // the SEST film's full path; null when off, missing or failed
        string pinned;        // ClipName= in the ini: this clip is swapped whether or not it loops
        string menuClip;      // without a pin, the first looping clip seen
        float nextScan;
        int unmatchedLogged;  // players logged that are not the menu film's; capped
        bool picturesOn;      // Pictures= in the ini, read with the rest
        PictureLog pictures;  // the stock-pictures log; null when off or stopped
        PictureSwap backdrops; // SEST photos in place of other backdrops; null when off or stopped

        void Awake()
        {
            try { Configure(); }
            catch (Exception e) { film = null; Debug.LogWarning(Tag + "not started: " + e.Message); }
            SceneManager.sceneLoaded += OnSceneLoaded;
            // The pictures log's periodic passes cover the first ten minutes.
            if (picturesOn) pictures = new PictureLog(Time.realtimeSinceStartup + 600f);
        }

        void OnSceneLoaded(Scene scene, LoadSceneMode mode)
        {
            float now = Time.realtimeSinceStartup;
            if (pictures != null)
            {
                pictures.Schedule(now + 2f, "scene '" + scene.name + "' +2s");
                pictures.Schedule(now + 20f, "scene '" + scene.name + "' +20s");
            }
        }

        void Update()
        {
            float now = Time.realtimeSinceStartup;
            if (now < nextScan) return;
            nextScan = now + 0.5f;
            if (film != null)
            {
                try
                {
                    Keep();
                    // Every half second for the whole session. The game builds
                    // the menu's player anew each time the main menu comes back
                    // (after a mission or a campaign, the Mod Manager, the
                    // editor) and coming back loads no scene, so a scan bounded
                    // to the first ten minutes and to scene loads left the
                    // stock film on after a long campaign (16 Oct 2026 test).
                    Scan();
                }
                catch (Exception e) { film = null; Debug.LogWarning(Tag + "stopped: " + e.Message); }
            }
            if (pictures != null)
            {
                try { pictures.Tick(now); }
                catch (Exception e) { pictures = null; Debug.LogWarning(PictureLog.Tag + "stopped: " + e.Message); }
            }
            if (backdrops != null)
            {
                try { backdrops.Tick(now); }
                catch (Exception e) { backdrops = null; Debug.LogWarning(PictureSwap.Tag + "stopped: " + e.Message); }
            }
        }

        void Scan()
        {
            VideoPlayer[] players = UnityEngine.Object.FindObjectsByType<VideoPlayer>(
                FindObjectsInactive.Include, FindObjectsSortMode.None);
            foreach (VideoPlayer vp in players)
            {
                // A player found before the game gives it its clip is looked at
                // again next time rather than written off for the session.
                if (vp == null || (vp.source == VideoSource.VideoClip && vp.clip == null)) continue;
                if (!seen.Add(vp.GetInstanceID())) continue;
                string clip = vp.clip != null ? vp.clip.name : "";
                bool menus = vp.source == VideoSource.VideoClip && vp.clip != null
                             && (!string.IsNullOrEmpty(pinned) ? clip == pinned : vp.isLooping);
                // Scanning all session, a mission that makes video players over
                // and over must not fill Player.log: the menu's own are always
                // written, the others up to fifty.
                if (!menus && ++unmatchedLogged > 50) continue;
                Debug.Log(Tag + "video player '" + PathOf(vp.transform) + "' in scene '" + vp.gameObject.scene.name
                          + "': source=" + vp.source + " clip='" + clip + "' url='" + vp.url + "' render="
                          + vp.renderMode + " loop=" + vp.isLooping + " playing=" + vp.isPlaying
                          + " audio=" + vp.audioOutputMode
                          + " tracks=" + (vp.clip != null ? vp.clip.audioTrackCount : 0));
                if (vp.source != VideoSource.VideoClip || vp.clip == null) continue;
                if (!string.IsNullOrEmpty(pinned))
                {
                    if (clip == pinned) Swap(vp);
                    continue;
                }
                if (!vp.isLooping) continue;
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
            var s = new Swapped { Player = vp, Clip = vp.clip, Loop = vp.isLooping, Audio = vp.audioOutputMode };
            if (vp.audioOutputMode == VideoAudioOutputMode.Direct && vp.clip.audioTrackCount > 0)
            {
                // The menu's music may be the clip's own sound track: it goes on
                // playing from the game's clip on a second player with no picture.
                var go = new GameObject("SEST Menu sound");
                go.transform.SetParent(vp.transform, false);
                VideoPlayer snd = go.AddComponent<VideoPlayer>();
                snd.playOnAwake = false;
                snd.source = VideoSource.VideoClip;
                snd.clip = vp.clip;
                snd.renderMode = VideoRenderMode.APIOnly;
                snd.audioOutputMode = VideoAudioOutputMode.Direct;
                snd.isLooping = true;
                for (ushort i = 0; i < vp.clip.audioTrackCount; i++)
                    snd.SetDirectAudioVolume(i, vp.GetDirectAudioVolume(i));
                s.Sound = snd;
                seen.Add(snd.GetInstanceID());   // a later scan must not take it for the menu's player
            }
            swapped.Add(s);
            Point(vp);
            Debug.Log(Tag + "menu film now " + film + (s.Sound != null ? "; the game's sound track kept" : ""));
        }

        void Point(VideoPlayer vp)
        {
            bool play = vp.isPlaying || vp.playOnAwake;
            vp.Stop();
            vp.source = VideoSource.Url;
            vp.url = film;
            vp.isLooping = true;
            vp.audioOutputMode = VideoAudioOutputMode.None;
            vp.errorReceived -= OnError;
            vp.errorReceived += OnError;
            if (play) vp.Play();
        }

        // After the swap: a player gone with its scene is forgotten, one the
        // game has pointed back at its clip gets the SEST film again, and the
        // kept sound track plays and pauses with the picture.
        void Keep()
        {
            for (int i = swapped.Count - 1; i >= 0; i--)
            {
                Swapped s = swapped[i];
                if (s.Player == null)
                {
                    if (s.Sound != null) Destroy(s.Sound.gameObject);
                    swapped.RemoveAt(i);
                    continue;
                }
                if (s.Player.source != VideoSource.Url || s.Player.url != film)
                {
                    Debug.Log(Tag + "the game set its clip again; back to the SEST film");
                    Point(s.Player);
                }
                if (s.Sound != null)
                {
                    if (s.Player.isPlaying && !s.Sound.isPlaying) s.Sound.Play();
                    else if (!s.Player.isPlaying && s.Sound.isPlaying) s.Sound.Pause();
                }
            }
        }

        // Unity could not play the SEST film: every swapped player gets the
        // game's clip back as it was, and the plugin stands down.
        void OnError(VideoPlayer vp, string message)
        {
            Debug.LogWarning(Tag + "the SEST film did not play (" + message + "); the game's own film is back");
            film = null;
            foreach (Swapped s in swapped)
            {
                if (s.Sound != null) Destroy(s.Sound.gameObject);
                if (s.Player == null) continue;
                s.Player.errorReceived -= OnError;
                s.Player.Stop();
                s.Player.source = VideoSource.VideoClip;
                s.Player.clip = s.Clip;
                s.Player.isLooping = s.Loop;
                s.Player.audioOutputMode = s.Audio;
                s.Player.Play();
            }
            swapped.Clear();
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
            // The pictures log is on unless Pictures=0; a missing film below
            // stops the swap, not the log.
            picturesOn = !(ini.TryGetValue("Pictures", out v) && v.Trim() == "0");
            if (!picturesOn) Debug.Log(Tag + "pictures log off (Pictures=0 in " + IniName + ")");
            // The backdrop swap is on unless Backdrops=0; it needs the pack's
            // own photographs, not the film.
            if (!(ini.TryGetValue("Backdrops", out v) && v.Trim() == "0"))
            {
                bool art = !(ini.TryGetValue("CampaignArt", out v) && v.Trim() == "0");
                try { backdrops = PictureSwap.Create(dir, art); }
                catch (Exception e) { backdrops = null; Debug.LogWarning(PictureSwap.Tag + "not started: " + e.Message); }
            }
            else Debug.Log(PictureSwap.Tag + "off (Backdrops=0 in " + IniName + ")");
            string name = ini.TryGetValue("Film", out v) && v.Trim().Length > 0 ? v.Trim() : "sest_menu.mp4";
            string path = Path.Combine(dir, name);
            if (!File.Exists(path)) throw new Exception("film not found: " + path);
            if (ini.TryGetValue("ClipName", out v) && v.Trim().Length > 0) pinned = v.Trim();
            film = path;
            Debug.Log(Tag + "ready: " + film + (pinned != null ? " for clip '" + pinned + "'" : ""));
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

        internal static string PathOf(Transform t)
        {
            string p = t.name;
            for (Transform u = t.parent; u != null; u = u.parent) p = u.name + "/" + p;
            return p;
        }
    }

    // The stock-pictures log. One pass writes, each line starting
    // "[SEST Pictures]":
    //   (a) every loaded Texture2D, RenderTexture and Sprite at least 256
    //       pixels each way (Resources.FindObjectsOfTypeAll), largest first:
    //       name, size, format;
    //   (b) every UnityEngine.UI Image or RawImage showing a texture. Those
    //       types are not in the reference package build_plugin.py compiles
    //       against (UnityEngine.Modules has no UnityEngine.UI), so they are
    //       found by name at run time;
    //   (c) NoesisGUI, the game's UI: from each NoesisView component's content
    //       down through Noesis' VisualTreeHelper, every Image or MediaElement
    //       and every element whose Background or Fill is an ImageBrush - the
    //       element's type and Name, the view it belongs to (the nearest
    //       ancestor that is a game class, say LoadScreenView), the Source
    //       (a BitmapImage's UriSource, a TextureSource's Unity texture), the
    //       property's binding path where BindingOperations.GetBinding has one
    //       (the review expects "BackgroundImage"), whether it is visible, its
    //       Opacity and its DataContext's type. Noesis is not referenced at
    //       compile time: all of it goes by reflection, and a member the
    //       game's build lacks is logged once ("skipped: ...") and passed over.
    // When: the first Update after start, 15 s later, every two minutes while
    // the ten-minute start window is open, 2 s and 20 s after each scene load
    // (scenes loading together share one pass), and once each time the Mod
    // Manager comes on screen - a Noesis element whose type or Name says
    // ModMenu or ModManager, looked for every 3 s while a scene named like
    // the menu's is loaded ('background', player.log 10 Oct 2026); at most
    // five such passes. Each part of a pass
    // writes at most 300 lines, then one "... N more" line; a pass walks at
    // most 20,000 Noesis elements. One part failing writes one line and the
    // others still run. Nothing is changed.
    public class PictureLog
    {
        public const string Tag = "[SEST Pictures] ";
        const int MinSize = 256;
        const int MaxLines = 300;
        const int MaxElements = 20000;
        const int ProbeElements = 3000;
        const int MaxModManagerPasses = 5;
        static readonly string[] BrushProps = { "Background", "Fill" };
        const BindingFlags Any = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static;

        class Due { public float At; public string Why; }
        struct Node { public object Element; public string Owner; }

        readonly List<Due> due = new List<Due>();
        readonly HashSet<string> skipped = new HashSet<string>();
        readonly Dictionary<string, Type> types = new Dictionary<string, Type>();
        readonly HashSet<string> absent = new HashSet<string>();   // component types not found; looked for again each pass
        readonly float periodicUntil;
        float nextPeriodic, nextProbe;
        bool started, modManagerUp;
        int passes, modManagerPasses, lines, dropped;

        public PictureLog(float startWindowEnd) { periodicUntil = startWindowEnd; }

        // A pass at the given time; scenes loading together share one.
        public void Schedule(float at, string why)
        {
            foreach (Due d in due) if (Mathf.Abs(d.At - at) < 1f) return;
            due.Add(new Due { At = at, Why = why });
        }

        // Called every half second by the swapper's Update: at most one pass
        // per call, else the Mod Manager probe.
        public void Tick(float now)
        {
            if (!started)
            {
                started = true;
                Schedule(now + 15f, "start +15s");
                nextPeriodic = now + 120f;
                Run("start", now);
                return;
            }
            for (int i = 0; i < due.Count; i++)
            {
                if (now < due[i].At) continue;
                string why = due[i].Why;
                due.RemoveAt(i);
                Run(why, now);
                return;
            }
            if (now <= periodicUntil && now >= nextPeriodic)
            {
                nextPeriodic = now + 120f;
                Run("periodic", now);
                return;
            }
            if (now >= nextProbe)
            {
                nextProbe = now + 3f;
                Probe(now);
            }
        }

        void Run(string why, float now)
        {
            passes++;
            absent.Clear();
            string head = "pass " + passes + " (" + why + ", " + now.ToString("F0") + " s after start)";
            Debug.Log(Tag + head + ":");
            int textures = 0, images = 0, views = 0, elements = 0, pictures = 0;
            string modManager = null;
            try { textures = LogTextures(); }
            catch (Exception e) { Debug.LogWarning(Tag + "textures not listed: " + e.Message); }
            try { images = LogUiImages(); }
            catch (Exception e) { Debug.LogWarning(Tag + "UI images not listed: " + e.Message); }
            try { views = LogNoesis(out elements, out pictures, out modManager); }
            catch (Exception e) { Debug.LogWarning(Tag + "Noesis views not listed: " + e.Message); }
            Debug.Log(Tag + head + " done: " + textures + " texture(s) of " + MinSize + " px or more, " + images + " UI image(s), "
                      + views + " Noesis view(s), " + elements + " element(s) walked, " + pictures + " picture element(s); Mod Manager "
                      + (modManager != null ? "on screen (" + modManager + ")" : "not seen"));
        }

        // (a) loaded textures, largest first.
        int LogTextures()
        {
            var items = new List<KeyValuePair<long, string>>();
            foreach (Texture2D t in Resources.FindObjectsOfTypeAll<Texture2D>())
                if (t != null && t.width >= MinSize && t.height >= MinSize)
                    items.Add(Item(t.width, t.height, "texture2d '" + t.name + "' " + t.width + "x" + t.height + " " + t.format));
            foreach (RenderTexture t in Resources.FindObjectsOfTypeAll<RenderTexture>())
                if (t != null && t.width >= MinSize && t.height >= MinSize)
                    items.Add(Item(t.width, t.height, "rendertexture '" + t.name + "' " + t.width + "x" + t.height + " " + t.format));
            foreach (Sprite s in Resources.FindObjectsOfTypeAll<Sprite>())
            {
                if (s == null) continue;
                int w = (int)s.rect.width, h = (int)s.rect.height;
                if (w >= MinSize && h >= MinSize)
                    items.Add(Item(w, h, "sprite '" + s.name + "' " + w + "x" + h + " of texture '" + (s.texture != null ? s.texture.name : "") + "'"));
            }
            items.Sort((a, b) => b.Key.CompareTo(a.Key));
            Begin();
            foreach (KeyValuePair<long, string> kv in items) Line(kv.Value);
            End("textures");
            return items.Count;
        }

        static KeyValuePair<long, string> Item(int w, int h, string line)
        {
            return new KeyValuePair<long, string>((long)w * h, line);
        }

        // (b) UnityEngine.UI images, by type name.
        int LogUiImages()
        {
            int n = 0;
            Begin();
            foreach (string typeName in new[] { "UnityEngine.UI.Image", "UnityEngine.UI.RawImage" })
            {
                Type t = FindType(typeName);
                if (t == null) { Skip(typeName + " (no such type is loaded)"); continue; }
                foreach (UnityEngine.Object o in UnityEngine.Object.FindObjectsByType(t, FindObjectsInactive.Include, FindObjectsSortMode.None))
                {
                    var c = o as Component;
                    var tex = Get(o, "mainTexture") as Texture;
                    if (c == null || tex == null) continue;
                    var sprite = Get(o, "sprite") as Sprite;
                    n++;
                    Line("ui " + t.Name + " '" + MenuFilmSwapper.PathOf(c.transform) + "' in scene '" + c.gameObject.scene.name
                         + "': texture '" + tex.name + "' " + tex.width + "x" + tex.height
                         + (sprite != null ? " sprite '" + sprite.name + "'" : "") + " active=" + c.gameObject.activeInHierarchy);
                }
            }
            End("UI images");
            return n;
        }

        // (c) the Noesis visual trees.
        int LogNoesis(out int elements, out int pictures, out string modManager)
        {
            elements = 0; pictures = 0; modManager = null;
            Type viewType; MethodInfo count, child;
            if (!NoesisApi(out viewType, out count, out child)) return 0;
            int views = 0;
            Begin();
            foreach (UnityEngine.Object o in UnityEngine.Object.FindObjectsByType(viewType, FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                var c = o as Component;
                object root = Root(o);
                views++;
                Line("noesis view '" + (c != null ? MenuFilmSwapper.PathOf(c.transform) : o.name) + "' in scene '"
                     + (c != null ? c.gameObject.scene.name : "") + "': content "
                     + (root != null ? root.GetType().Name + " '" + Name(root) + "' DataContext=" + TypeName(Get(root, "DataContext")) : "null"));
                if (root == null) continue;
                var stack = new Stack<Node>();
                stack.Push(new Node { Element = root, Owner = root.GetType().Name });
                while (stack.Count > 0 && elements < MaxElements)
                {
                    Node n = stack.Pop();
                    elements++;
                    string type = n.Element.GetType().Name;
                    string owner = IsGameType(n.Element) ? type : n.Owner;
                    if (modManager == null && LooksLikeModManager(n.Element, type)) modManager = type + " '" + Name(n.Element) + "'";
                    if (Inspect(n.Element, type, owner)) pictures++;
                    foreach (object ch in Children(n.Element, count, child)) stack.Push(new Node { Element = ch, Owner = owner });
                }
                if (elements >= MaxElements) Debug.Log(Tag + "walk stopped at " + MaxElements + " elements");
            }
            End("Noesis elements");
            return views;
        }

        // Writes the element when it shows a picture: an Image or MediaElement,
        // or a Background or Fill that is an ImageBrush.
        bool Inspect(object el, string type, string owner)
        {
            bool hit = false;
            if (Derives(el, "Image") || Derives(el, "MediaElement"))
            {
                Line("noesis " + type + " '" + Name(el) + "' in " + owner + ": Source=" + Describe(Need(el, "Source"))
                     + Binding(el, "Source") + State(el));
                hit = true;
            }
            foreach (string prop in BrushProps)
            {
                object brush = Get(el, prop);
                if (brush == null || brush.GetType().Name != "ImageBrush") continue;
                Line("noesis " + type + " '" + Name(el) + "' in " + owner + ": " + prop + "=ImageBrush ImageSource="
                     + Describe(Need(brush, "ImageSource")) + Binding(brush, "ImageSource") + Binding(el, prop) + State(el));
                hit = true;
            }
            return hit;
        }

        // An ImageSource: a BitmapImage by its UriSource, a TextureSource by
        // its Unity texture, anything else by its ToString and size.
        string Describe(object src)
        {
            if (src == null) return "null";
            string t = src.GetType().Name;
            object uri = Get(src, "UriSource");
            if (uri != null) return t + " '" + uri + "'";
            var tex = Get(src, "Texture") as Texture;
            if (tex != null) return t + " texture '" + tex.name + "' " + tex.width + "x" + tex.height;
            object w = Get(src, "Width"), h = Get(src, "Height");
            return t + " '" + src + "'" + (w != null && h != null ? " " + w + "x" + h : "");
        }

        // " <prop> bound to '<path>'" when the dependency property has a
        // binding, "" when it has none or Noesis cannot be asked.
        string Binding(object target, string prop)
        {
            try
            {
                object dp = DependencyProperty(target.GetType(), prop + "Property");
                if (dp == null) { Skip(target.GetType().Name + "." + prop + "Property (no such dependency property)"); return ""; }
                Type ops = FindType("Noesis.BindingOperations");
                MethodInfo get = ops != null ? Method(ops, "GetBinding", 2) : null;
                if (get == null) { Skip("Noesis.BindingOperations.GetBinding (no such method)"); return ""; }
                object b = get.Invoke(null, new object[] { target, dp });
                if (b == null) return "";
                object path = Get(b, "Path");
                object text = path != null ? Get(path, "Path") : null;
                return " " + prop + " bound to '" + (text ?? path ?? b) + "'";
            }
            catch (Exception e) { Skip("GetBinding " + target.GetType().Name + "." + prop + ": " + Inner(e)); return ""; }
        }

        string State(object el)
        {
            return " visible=" + Str(Get(el, "IsVisible")) + " opacity=" + Str(Get(el, "Opacity"))
                   + " DataContext=" + TypeName(Get(el, "DataContext"));
        }

        // The element's visual children through VisualTreeHelper, last first
        // so a stack walks them in order.
        List<object> Children(object el, MethodInfo count, MethodInfo child)
        {
            var list = new List<object>();
            int k;
            try { k = (int)count.Invoke(null, new object[] { el }); }
            catch (Exception e) { Skip("VisualTreeHelper.GetChildrenCount on " + el.GetType().Name + ": " + Inner(e)); return list; }
            for (int i = k - 1; i >= 0; i--)
            {
                try
                {
                    object ch = child.Invoke(null, new object[] { el, i });
                    if (ch != null) list.Add(ch);
                }
                catch (Exception e) { Skip("VisualTreeHelper.GetChild on " + el.GetType().Name + ": " + Inner(e)); break; }
            }
            return list;
        }

        // A NoesisView's content: its Content, else its View's Content.
        object Root(object view)
        {
            object root = Get(view, "Content");
            if (root == null)
            {
                object v = Get(view, "View");
                if (v != null) root = Get(v, "Content");
            }
            if (root == null && Prop(view.GetType(), "Content") == null && Prop(view.GetType(), "View") == null)
                Skip(view.GetType().Name + ".Content and .View (no such members)");
            return root;
        }

        bool NoesisApi(out Type viewType, out MethodInfo count, out MethodInfo child)
        {
            count = null; child = null;
            viewType = FindComponentType("NoesisView");
            Type helper = FindType("Noesis.VisualTreeHelper");
            if (viewType == null) Skip("NoesisView (no such component type is loaded)");
            if (helper == null) Skip("Noesis.VisualTreeHelper (no such type is loaded)");
            if (viewType == null || helper == null) return false;
            count = Method(helper, "GetChildrenCount", 1);
            child = Method(helper, "GetChild", 2);
            if (count == null) Skip("Noesis.VisualTreeHelper.GetChildrenCount (no such method)");
            if (child == null) Skip("Noesis.VisualTreeHelper.GetChild (no such method)");
            return count != null && child != null;
        }

        // Every 3 s while a scene named like the menu's is loaded: a
        // breadth-first look through the Noesis views for a Mod Manager
        // element, and one pass when it has just appeared.
        void Probe(float now)
        {
            if (!MenuSceneLoaded()) { modManagerUp = false; return; }
            Type viewType; MethodInfo count, child;
            if (!NoesisApi(out viewType, out count, out child)) return;
            string found = null;
            int seen = 0;
            foreach (UnityEngine.Object o in UnityEngine.Object.FindObjectsByType(viewType, FindObjectsInactive.Include, FindObjectsSortMode.None))
            {
                object root = Root(o);
                if (root == null) continue;
                var queue = new Queue<object>();
                queue.Enqueue(root);
                while (queue.Count > 0 && found == null && seen < ProbeElements)
                {
                    object el = queue.Dequeue();
                    seen++;
                    string type = el.GetType().Name;
                    if (LooksLikeModManager(el, type)) { found = type + " '" + Name(el) + "'"; break; }
                    foreach (object ch in Children(el, count, child)) queue.Enqueue(ch);
                }
                if (found != null) break;
            }
            if (found == null) { modManagerUp = false; return; }
            if (modManagerUp) return;
            modManagerUp = true;
            if (modManagerPasses < MaxModManagerPasses) { modManagerPasses++; Run("Mod Manager on screen: " + found, now); }
            else Skip("further Mod Manager passes (" + MaxModManagerPasses + " written)");
        }

        static bool MenuSceneLoaded()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                string n = SceneManager.GetSceneAt(i).name;
                if (n == null) continue;
                n = n.ToLowerInvariant();
                if (n.Contains("background") || n.Contains("menu")) return true;
            }
            return false;
        }

        // The Mod Manager's own view, by type or Name; the main menu's button
        // to it (ButtonModManager_Click in the XAML) does not count.
        static bool LooksLikeModManager(object el, string type)
        {
            string t = type.ToLowerInvariant();
            if (t.Contains("modmenu") || t.Contains("modmanager")) return true;
            if (t.Contains("button") || t.Contains("text") || t == "run") return false;
            string n = Name(el).ToLowerInvariant();
            return n.Contains("modmenu") || n.Contains("modmanager");
        }

        // --- line budget and the once-per-run notes ---------------------------
        void Begin() { lines = 0; dropped = 0; }
        void Line(string s) { if (++lines <= MaxLines) Debug.Log(Tag + s); else dropped++; }
        void End(string what) { if (dropped > 0) Debug.Log(Tag + "... " + dropped + " more " + what); }
        void Skip(string what) { if (skipped.Add(what)) Debug.Log(Tag + "skipped: " + what); }

        // --- reflection, every call guarded -----------------------------------
        static string Name(object el) { return (Get(el, "Name") as string) ?? ""; }
        static string TypeName(object o) { return o == null ? "null" : o.GetType().Name; }
        static string Str(object o) { return o == null ? "?" : o.ToString(); }

        static string Inner(Exception e)
        {
            return e is TargetInvocationException && e.InnerException != null ? e.InnerException.Message : e.Message;
        }

        // A game class, as against one of Noesis' own: the view a picture
        // belongs to.
        static bool IsGameType(object el)
        {
            string ns = el.GetType().Namespace;
            return ns == null || !ns.StartsWith("Noesis");
        }

        static bool Derives(object el, string noesisType)
        {
            for (Type t = el.GetType(); t != null; t = t.BaseType)
                if (t.Name == noesisType && t.Namespace == "Noesis") return true;
            return false;
        }

        // A property by name; the most derived one when a type hides another's.
        static PropertyInfo Prop(Type t, string name)
        {
            try { return t.GetProperty(name, Any); }
            catch (AmbiguousMatchException)
            {
                foreach (PropertyInfo p in t.GetProperties(Any)) if (p.Name == name) return p;
                return null;
            }
        }

        // A property's value, null when the object has no such property or
        // reading it throws.
        static object Get(object o, string prop)
        {
            if (o == null) return null;
            try
            {
                PropertyInfo p = Prop(o.GetType(), prop);
                return p != null && p.CanRead ? p.GetValue(o, null) : null;
            }
            catch (Exception) { return null; }
        }

        // The same, for a member the pass counts on: missing or failing, it is
        // noted once.
        object Need(object o, string prop)
        {
            if (o == null) return null;
            PropertyInfo p = Prop(o.GetType(), prop);
            if (p == null || !p.CanRead) { Skip(o.GetType().Name + "." + prop + " (no such member)"); return null; }
            try { return p.GetValue(o, null); }
            catch (Exception e) { Skip(o.GetType().Name + "." + prop + ": " + Inner(e)); return null; }
        }

        static object DependencyProperty(Type t, string name)
        {
            const BindingFlags f = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.FlattenHierarchy;
            PropertyInfo p = t.GetProperty(name, f);
            if (p != null) return p.GetValue(null, null);
            FieldInfo fi = t.GetField(name, f);
            return fi != null ? fi.GetValue(null) : null;
        }

        static MethodInfo Method(Type t, string name, int args)
        {
            foreach (MethodInfo m in t.GetMethods(Any))
                if (m.Name == name && m.GetParameters().Length == args) return m;
            return null;
        }

        Type FindType(string fullName)
        {
            Type t;
            if (types.TryGetValue(fullName, out t)) return t;
            foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
            {
                try { t = a.GetType(fullName, false); }
                catch (Exception) { t = null; }
                if (t != null) { types[fullName] = t; return t; }
            }
            return null;
        }

        // A MonoBehaviour by its bare name, any namespace, any assembly but
        // the runtime's own. Reading every assembly's types is the one costly
        // lookup here, so a miss is remembered until the next pass.
        Type FindComponentType(string name)
        {
            Type t;
            if (types.TryGetValue(name, out t)) return t;
            if (absent.Contains(name)) return null;
            foreach (Assembly a in AppDomain.CurrentDomain.GetAssemblies())
            {
                string an = a.GetName().Name ?? "";
                if (an.StartsWith("System") || an.StartsWith("mscorlib") || an.StartsWith("UnityEngine") || an.StartsWith("Unity.")) continue;
                Type[] all;
                try { all = a.GetTypes(); }
                catch (ReflectionTypeLoadException e) { all = e.Types; }
                catch (Exception) { continue; }
                foreach (Type c in all)
                    if (c != null && c.Name == name && typeof(MonoBehaviour).IsAssignableFrom(c)) { types[name] = c; return c; }
            }
            absent.Add(name);
            return null;
        }
    }

    // SEST photographs in place of every other backdrop picture. The game
    // names a texture it loads from a file by the file's full path; one whose
    // path runs through a ui/backgrounds folder (or, with CampaignArt, a
    // campaigns or missions folder) and not through the SEST pack is a
    // backdrop from the base game or another mod. Each is painted over once
    // with one of the pack's own photographs (its ui/backgrounds pictures),
    // picked by the texture's name so the same picture always gets the same
    // photo, cropped to its shape and scaled to its size, and written back
    // into the same texture: whatever the game's UI shows it in shows the
    // photo. A texture that cannot be written (not readable, compressed) is
    // left as it is and named once in the log. Looked for every second for
    // the whole session: the game loads a backdrop when it first shows it.
    public class PictureSwap
    {
        public const string Tag = "[SEST Backdrops] ";
        const int MaxLogged = 200;

        readonly List<string> photos = new List<string>();
        readonly HashSet<int> done = new HashSet<int>();
        readonly bool campaignArt;
        float next;
        int swappedCount, logged;

        PictureSwap(List<string> files, bool art) { photos = files; campaignArt = art; }

        // The pack's photographs: ui/backgrounds beside the plugins folder.
        public static PictureSwap Create(string pluginDir, bool art)
        {
            string pack = Directory.GetParent(pluginDir).FullName;
            string dir = Path.Combine(Path.Combine(pack, "ui"), "backgrounds");
            var files = new List<string>();
            if (Directory.Exists(dir))
                foreach (string f in Directory.GetFiles(dir))
                {
                    string e = Path.GetExtension(f).ToLowerInvariant();
                    if (e == ".png" || e == ".jpg" || e == ".jpeg") files.Add(f);
                }
            files.Sort(StringComparer.OrdinalIgnoreCase);
            if (files.Count == 0) throw new Exception("no SEST photographs in " + dir);
            Debug.Log(Tag + "ready: " + files.Count + " SEST photographs from " + dir
                      + (art ? "; campaign and mission pictures included" : "; campaign and mission pictures left alone"));
            return new PictureSwap(files, art);
        }

        public void Tick(float now)
        {
            if (now < next) return;
            next = now + 1f;
            foreach (Texture2D t in Resources.FindObjectsOfTypeAll<Texture2D>())
            {
                if (t == null || !done.Add(t.GetInstanceID())) continue;
                if (!Wanted(t.name)) continue;
                Paint(t);
            }
        }

        // A file path through a backdrop folder, not the SEST pack's.
        bool Wanted(string name)
        {
            if (string.IsNullOrEmpty(name) || name.Length < 8) return false;
            string n = name.Replace('\\', '/').ToLowerInvariant();
            if (n.IndexOf(":/", StringComparison.Ordinal) < 0 && !n.StartsWith("/")) return false;   // not a file
            if (!(n.EndsWith(".png") || n.EndsWith(".jpg") || n.EndsWith(".jpeg"))) return false;
            if (n.Contains("/sest_integration/") || n.Contains("/3812461539/")) return false;
            if (n.Contains("/ui/backgrounds/")) return true;
            if (!campaignArt || n.Contains("/user/")) return false;
            return n.Contains("/campaigns/") || n.Contains("/missions/");
        }

        void Paint(Texture2D target)
        {
            string photo = photos[(int)((uint)StableHash(target.name) % (uint)photos.Count)];
            try
            {
                if (!target.isReadable) { Note("left as it is (not readable): " + target.name); return; }
                var src = new Texture2D(2, 2, TextureFormat.RGB24, false);
                try
                {
                    if (!ImageConversion.LoadImage(src, File.ReadAllBytes(photo), false))
                    { Note("photo not read: " + photo); return; }
                    Color32[] pixels = Fit(src.GetPixels32(), src.width, src.height, target.width, target.height);
                    target.SetPixels32(pixels);
                    target.Apply(false);
                }
                finally { UnityEngine.Object.Destroy(src); }
                swappedCount++;
                Note("SEST photo " + Path.GetFileName(photo) + " in place of " + target.name
                     + " (" + target.width + "x" + target.height + "); " + swappedCount + " so far");
            }
            catch (Exception e) { Note("left as it is (" + e.Message + "): " + target.name); }
        }

        // The photo cropped to the target's shape around its centre, then
        // scaled to its size (nearest pixel; rows bottom-up, as Unity's are).
        static Color32[] Fit(Color32[] src, int sw, int sh, int tw, int th)
        {
            double want = (double)tw / th, have = (double)sw / sh;
            int cw = sw, ch = sh, cx = 0, cy = 0;
            if (have > want) { cw = Math.Max(1, (int)Math.Round(sh * want)); cx = (sw - cw) / 2; }
            else if (have < want) { ch = Math.Max(1, (int)Math.Round(sw / want)); cy = (sh - ch) / 2; }
            var dst = new Color32[tw * th];
            for (int y = 0; y < th; y++)
            {
                int sy = cy + (int)((long)y * ch / th);
                int row = sy * sw, drow = y * tw;
                for (int x = 0; x < tw; x++)
                    dst[drow + x] = src[row + cx + (int)((long)x * cw / tw)];
            }
            return dst;
        }

        // FNV-1a of the lower-case name: the same picture gets the same photo
        // in every session.
        static int StableHash(string s)
        {
            unchecked
            {
                uint h = 2166136261;
                foreach (char c in s.ToLowerInvariant()) { h ^= c; h *= 16777619; }
                return (int)h;
            }
        }

        void Note(string s)
        {
            if (logged < MaxLogged) Debug.Log(Tag + s);
            else if (logged == MaxLogged) Debug.Log(Tag + "further lines not written");
            logged++;
        }
    }
}
