using System;
using System.Linq.Expressions;
using System.Reflection;
using System.Runtime.CompilerServices;

namespace Sest.RuntimeFixes
{
    internal static class TerrainClearance
    {
        static Type missile;
        static Func<object, object> ammunition, geo, transform;
        static Func<object, string> roundName, stage;
        static Func<object, bool> terrainFollowing;
        static Func<object, float> heading;
        static Func<object, float, float, float> highest;
        static float clearance;
        static bool active, reported;
        sealed class Match { internal bool Mst; }
        static readonly ConditionalWeakTable<object, Match> rounds = new ConditionalWeakTable<object, Match>();

        internal static MethodInfo Bind(Assembly game)
        {
            Type obj = Api.Type(game, "SeaPower.ObjectBase"), weapon = Api.Type(game, "SeaPower.WeaponBase");
            Type ap = Api.Type(game, "SeaPower.AmmunitionParameters"), terrain = Api.Type(game, "SeaPower.TerrainUtils");
            missile = Api.Type(game, "SeaPower.Missile");
            ammunition = Getter<object>(weapon, "_ap");
            roundName = Getter<string>(ap, "_ammunitionFileName");
            terrainFollowing = Getter<bool>(ap, "_terrainFollowFlight");
            geo = Getter<object>(obj, "_geoPosition");
            transform = Getter<object>(obj, "transform");
            PropertyInfo stageProperty = weapon.GetProperty("_flightStage", Api.All);
            if (stageProperty == null || !stageProperty.PropertyType.IsEnum) throw new MissingMemberException("_flightStage enum");
            Type stageType = stageProperty.PropertyType;
            foreach (string name in new[] { "ToBearing", "MaintainHeight", "MoveToLoftAlt", "MaintainLoftAlt",
                "MoveToSeaSkimming", "MaintainSeaSkimming", "MoveToFinalFlightAlt", "MaintainFinalFlightAlt",
                "AlignSensorToTarget", "TerminalApproach" })
                if (!Enum.IsDefined(stageType, name)) throw new MissingMemberException(stageType.Name, name);
            Func<object, object> stageValue = Getter<object>(weapon, "_flightStage");
            stage = value => Enum.GetName(stageType, stageValue(value));
            Type transformType = obj.GetProperty("transform", Api.All).PropertyType;
            var input = Expression.Parameter(typeof(object), "transform");
            var angles = Expression.Property(Expression.Convert(input, transformType), "eulerAngles");
            heading = Expression.Lambda<Func<object, float>>(Expression.Field(angles, "y"), input).Compile();
            Type geoType = obj.GetProperty("_geoPosition", Api.All).PropertyType;
            MethodInfo ahead = Api.Method(terrain, "CrudeGetHighestTerrainHeightAhead", typeof(float),
                geoType, typeof(float), typeof(float), typeof(bool));
            var position = Expression.Parameter(typeof(object), "geo");
            var bearing = Expression.Parameter(typeof(float), "heading");
            var distance = Expression.Parameter(typeof(float), "distance");
            highest = Expression.Lambda<Func<object, float, float, float>>(Expression.Call(ahead,
                Expression.Convert(position, geoType), bearing, distance, Expression.Constant(false)), position, bearing, distance).Compile();
            clearance = (float)Api.Method(Api.Type(game, "SeaPower.Utils"), "heightInFeetToUnity", typeof(float),
                typeof(float)).Invoke(null, new object[] { Policy.LandClearanceFeet });
            if (!Policy.Finite(clearance) || clearance <= 0) throw new InvalidOperationException("invalid altitude conversion");
            active = true;
            return Api.Method(terrain, "GetSafeAltitudeOverSurface", typeof(float), obj, typeof(float),
                typeof(float), typeof(bool), typeof(bool));
        }

        static Func<object, T> Getter<T>(Type type, string name)
        {
            var input = Expression.Parameter(typeof(object), "instance");
            var value = Expression.PropertyOrField(Expression.Convert(input, type), name);
            return Expression.Lambda<Func<object, T>>(Expression.Convert(value, typeof(T)), input).Compile();
        }

        internal static void Install(Assembly game)
        {
            MethodInfo target = Bind(game);
            Api.Postfix(target, typeof(TerrainClearance), "Postfix", "io.github.sest-hobby.mst-terrain");
            Api.Log("MST terrain correction installed: RGM/UGM-109E5a cruise only, 500 ft over land ahead; native terminal profile retained");
        }

        internal static void Postfix(object __0, bool __4, ref float __result)
        {
            if (!active || !__4 || __0 == null || !missile.IsInstanceOfType(__0)) return;
            try
            {
                object ap = ammunition(__0);
                if (ap == null || !terrainFollowing(ap)) return;
                if (!rounds.GetValue(ap, key => new Match { Mst = Policy.IsMst(roundName(key)) }).Mst) return;
                if (!Policy.CruiseStage(stage(__0))) return;
                float land = highest(geo(__0), heading(transform(__0)), Policy.LookAheadNm);
                float result = Policy.Altitude(__result, land, clearance);
                if (result > __result && !reported)
                {
                    reported = true;
                    Api.Log("MST land clearance applied; terrain remains collidable and missile uses native pitch/turn limits");
                }
                __result = result;
            }
            catch (Exception e)
            {
                active = false;
                Api.LogFailure("terrain correction disabled for this session; native result retained", e);
            }
        }
    }
}
