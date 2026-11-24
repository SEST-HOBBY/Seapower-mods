// Kept apart from BetaCompatibilityCalls.cs and fully qualified: the build's
// global usings include System.IO, and adding `using Noesis; using MapControl;`
// to the shared file invites simple-name clashes (Noesis.Path and others).
namespace AnchorChain;

public static partial class BetaCompatibilityCalls
{
    // DCM 1.0.2 on 261123: CampaignMain.GetVisualPostureAndColour(Side) as it
    // was in 261116. Blue gives Allied + FriendlyColor, Red gives Enemy +
    // HostileColor, anything else Neutral + NeutralColor, all with the day brush.
    // The posture half is the native 261123 CampaignMain.GetVisualPosture.
    public static System.ValueTuple<SeapowerUI.MapVisualPosture, Noesis.SolidColorBrush> CampaignSideLook(SeapowerUI.ViewModels.MissionEditorViewModel.Side side)
    {
        SeapowerUI.MapVisualPosture posture = SeaPower.CampaignMain.GetVisualPosture(side);
        string key = posture == SeapowerUI.MapVisualPosture.Allied ? "FriendlyColor" :
            posture == SeapowerUI.MapVisualPosture.Enemy ? "HostileColor" : "NeutralColor";
        return new System.ValueTuple<SeapowerUI.MapVisualPosture, Noesis.SolidColorBrush>(posture, SeaPower.UI_Parameters.MapBrush(key, false));
    }

    // 261123 groups hold no brush: the map colours them from VisualPosture
    // (which DCM sets) and the side override. DCM's contact fade (a
    // translucent copy of the side brush) has no native home and is dropped.
    // A null group fails as the callvirt did.
    public static void CampaignGroupBrush(SeapowerUI.ViewModels.GroupOfUnits group, Noesis.Brush brush)
    {
        if (group == null) throw new System.NullReferenceException();
    }

    // MapDrawingLayer now needs the state manager that drives its eraser and
    // hover checks, and the frame it measures in. DCM pushes its tools onto the
    // campaign view's manager; the game's own campaign map uses Equirectangular.
    public static SeapowerUI.ViewModels.MapDrawingLayer NewCampaignDrawingLayer()
    {
        SeapowerUI.ViewModels.InteractionStateManager states = null;
        if (SeaPower.Singleton<SeapowerUI.ViewModels.CampaignViewModel>.InstanceExists(false)) {
            var campaign = SeaPower.Singleton<SeapowerUI.ViewModels.CampaignViewModel>.Instance;
            if (campaign != null) states = campaign.StateManager;
        }
        if (states == null) throw new System.InvalidOperationException("No campaign view state manager for the campaign drawing layer");
        return new SeapowerUI.ViewModels.MapDrawingLayer(states, SeaPower.GridFrame.Equirectangular);
    }

    // MapControl.MapTileLayer (the flat campaign tiles) no longer exists; no
    // background element of the 261123 campaign map is one.
    public static Noesis.BaseComponent CampaignFlatTileLayer(System.Collections.IEnumerable background)
    {
        if (background == null) throw new System.ArgumentNullException("source");
        return null;
    }

    // GlobeMap.Fail disposes only the globe DCM made ("DCM campaign"), never
    // the game's own 261123 campaign globe ("DynamicCampaign") on the same view.
    public static MapControl.MapInstance CampaignGlobeToDispose(SeapowerUI.MapViewModel map)
    {
        MapControl.MapInstance current = map.Instance;
        return current != null && current.Name == "DCM campaign" ? current : null;
    }
}

