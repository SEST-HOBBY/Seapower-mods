namespace Sest.UiFixes
{
    // UI events request a mode change. The controller commits it on its next
    // update, after the routed click has finished traversing the old controls.
    public sealed class FormationModeState
    {
        public bool Stock { get; private set; }
        public bool? Pending { get; private set; }
        public void Restore(string value) { Stock = value != null && value.Trim() == "stock"; Pending = null; }
        public void Toggle() { Pending = !(Pending ?? Stock); }
        public bool Commit()
        {
            if (!Pending.HasValue) return false;
            bool changed = Stock != Pending.Value;
            Stock = Pending.Value; Pending = null;
            return changed;
        }
        public string Encode() { return Stock ? "stock" : "enhanced"; }
    }
}
