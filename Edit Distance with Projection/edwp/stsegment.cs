using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Numerics;

namespace edwp
{
    public class stsegment
    {
        public stsegment(stpoint s1, stpoint s2)
        {
            _s1 = s1;
            _s2 = s2;
            length = calclen();
        }

        public stsegment(float x1, float y1, double t1, float x2, float y2, double t2)
        {
            _s1 = new stpoint(x1, y1, t1);
            _s2 = new stpoint(x2, y2, t2);
            length = calclen();
        }

        stpoint _s1, _s2;
        public float length;
        public stpoint s1 { get { return _s1; } set { _s1 = value; checkinvariant(); length = calclen(); } }
        public stpoint s2 { get { return _s2; } set { _s2 = value; checkinvariant(); length = calclen(); } }

        public float calclen()
        {
            return _s1.dist(_s2);
        }

        // s1.t must NOT be larger than s2.t
        void checkinvariant()
        {
            if (_s1.t > s2.t)
                throw new ArgumentException(string.Format("s1.t > s2.t. s1: {0} s2: {0}", _s1, _s2));
        }

        public float speed { get { if (s2.t == s1.t) return 0; return length / (float)(s2.t - s1.t); } }

        // gets the vector projection of pt on this segment, clamped
        public stpoint getProjection(stpoint pt)
        {
            // center the problem
            Vector2 ap = pt.xy - s1.xy;
            Vector2 ab = s2.xy - s1.xy;
            float ablen = ab.Length();
            // if ablen is zero, quit
            if (ablen == 0)
            {
                return new stpoint(s1.xy, s1.t);
            }
            float plen = Vector2.Dot(ab, ap) / ablen;
            if (plen < 0) plen = 0;
            else if (plen > ablen) plen = ablen;
            ap = ab * plen / ablen; // store the result in ap
            if (speed == 0)
            {
                return new stpoint(ap, pt.t);
            }
            double time = _s1.t + Vector2.Distance(ap, s1.xy) / speed;
            return new stpoint(ap, time);
        }

        public override string ToString()
        {
            return string.Format("{{{0} -> {1}}}", _s1, _s2);
        }
    }
}
