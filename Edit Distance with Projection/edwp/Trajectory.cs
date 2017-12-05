using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace edwp
{
    public class Trajectory
    {
        public Trajectory(List<stsegment> segments)
        {
            this.segments = segments;
        }

        public Trajectory(List<stpoint> points)
        {
            segments = new List<stsegment>();
            for(int i = 1; i < points.Count; i++)
            {
                segments.Add(new stsegment(points[i - 1], points[i]));
            }
        }

        public List<stsegment> segments;

        public stsegment this[int index]
        {
            get { return segments[index]; }
            set { segments[index] = value; }
        }

        public int Count { get { return segments.Count; } }

        public override string ToString()
        {
            var s = new StringBuilder("Trajectory<");
            int c = Count;
            for(int i = 0; i < c; i++)
            {
                if (i == 0)
                    s.Append(segments[0].ToString());
                else
                {
                    s.Append("           ");
                    s.Append(segments[i].ToString());
                }
                if (i != c - 1) // skip appending newline if last segment
                    s.Append("\n");
            }
            s.Append(">");
            return s.ToString();
        }

        // Calculates the sum of all segment lengths
        public float getTrajectoryLength()
        {
            float sum = 0;
            foreach(var seg in segments)
            {
                sum += seg.length;
            }
            return sum;
        }

        // clone this trajectory and replace the first segment with the two provided ones.
        public Trajectory insertAndClone(stsegment newseg1, stsegment newseg2)
        {
            var list = new List<stsegment>(Count);
            list.Add(newseg1);
            list.Add(newseg2);
            list.Concat(segments.Skip(1));
            return new Trajectory(list);
        }

        // aka rep(,). Calculates the cost of matching
        public float replace(Trajectory other)
        {
            float d1 = this[0].s1.dist(other[0].s1);
            float d2 = this[0].s2.dist(other[0].s2);
            return d1 + d1;
        }

        // Returns a copy of this trajectory minus the first element.
        public Trajectory rest()
        {
            return new Trajectory(segments.Skip(1).ToList());
        }

        public float coverage(Trajectory other)
        {
            return this[0].length + other[0].length;
        }

        public Trajectory insert(Trajectory other)
        {
            stsegment e1 =  this[0];
            stsegment e2 = other[0];
            // if inserting onto a segment of len 0, return without calculating
            if (e1.s1 == e1.s2)
                return insertAndClone(e1, e1);
            stpoint pt = e1.getProjection(e2.s2);
            stsegment newseg1 = new stsegment(e1.s1, pt);
            stsegment newseg2 = new stsegment(pt, e1.s2);
            return insertAndClone(newseg1, newseg2);
        }
    }
}
