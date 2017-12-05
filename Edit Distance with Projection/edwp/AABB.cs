using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;

namespace edwp
{
    public class AABB
    {
        public AABB(float xmin, float xmax, float ymin, float ymax)
        {
            topleft = new Vector2(xmin, ymin);
            bottomright = new Vector2(xmax, ymax);
        }

        public AABB(Vector2 topleft, Vector2 bottomright)
        {
            this.topleft = topleft;
            this.bottomright = bottomright;
        }

        public AABB(Trajectory traj)
        {
            topleft = new Vector2(float.MaxValue, float.MaxValue);
            bottomright = new Vector2(float.MinValue, float.MinValue);
            // find the extremities of traj
            foreach(var seg in traj.segments)
            {
                // doing python things in C# :fine:
                foreach(var pt in new stpoint[] { seg.s1, seg.s2 })
                {
                    if (pt.xy.X < topleft.X)
                        topleft.X = pt.xy.X;
                    if (bottomright.X < pt.xy.X)
                        bottomright.X = pt.xy.X;
                    if (pt.xy.Y < topleft.Y)
                        topleft.Y = pt.xy.Y;
                    if (bottomright.Y < pt.xy.Y)
                        bottomright.Y = pt.xy.Y;
                }
            }
        }

        public Vector2 topleft, bottomright;

        public bool IsBounded(Vector2 point)
        {
            bool x = topleft.X < point.X && point.X < bottomright.X;
            bool y = topleft.Y < point.Y && point.Y < bottomright.Y;
            return x && y;
        }

        public static bool Intersects(AABB aabb1, AABB aabb2)
        {
            // an AABB intersects another if at least one corner is within the other.
            if (aabb2.IsBounded(aabb1.topleft))
                return true;
            if (aabb2.IsBounded(aabb1.bottomright))
                return true;
            return false;
        }

        // basically a Trajectory.replace() between aabb1 and aabb2
        public static float ReplacementDistance(AABB aabb1, AABB aabb2)
        {
            float d1 = Vector2.Distance(aabb1.topleft, aabb2.topleft);
            float d2 = Vector2.Distance(aabb1.bottomright, aabb2.bottomright);
            return d1 + d2;
        }

        public static float Coverage(AABB aabb1, AABB aabb2)
        {
            float d1 = (aabb1.topleft - aabb1.bottomright).Length();
            float d2 = (aabb2.topleft - aabb2.bottomright).Length();
            return d1 + d2;
        }
    }
}
