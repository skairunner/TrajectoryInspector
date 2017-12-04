using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;

namespace edwp
{
    public class stpoint: IEquatable<stpoint>
    {
        public stpoint(float x, float y, double t)
        {
            this.t = t;
            xy = new Vector2(x, y);
        }

        public stpoint(Vector2 xy, double t)
        {
            this.t = t;
            this.xy = xy;
        }

        public Vector2 xy;
        public double t;

        public float dist(stpoint other)
        {
            return Vector2.Distance(xy, other.xy);
        }

        public float dist2(stpoint other)
        {
            return Vector2.DistanceSquared(xy, other.xy);
        }

        override public string ToString()
        {
            return string.Format("({0:F2}, {1:F2}, {2:F2})", xy.X, xy.Y, t);
        }

        public bool Equals(stpoint other)
        {
            return xy == other.xy && t == other.t;
        }

        public static bool operator==(stpoint left, stpoint right)
        {
            return left.xy == right.xy && left.t == right.t;
        }

        public static bool operator !=(stpoint left, stpoint right)
        {
            return left.xy != right.xy || left.t != right.t;
        }

        public bool equivalent(stpoint other, float epsilon = 0.0001f)
        {
            if (xy.X - other.xy.X > epsilon) return false;
            if (xy.Y - other.xy.Y > epsilon) return false;
            if (t - other.t > epsilon) return false;
            return true;
        }
    }
}
