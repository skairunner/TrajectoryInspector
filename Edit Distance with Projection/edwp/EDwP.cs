using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace edwp
{
    class EDwP
    {
        public static float averager(Trajectory traj1, Trajectory traj2, float val)
        {
            return val / (traj1.getTrajectoryLength() + traj2.getTrajectoryLength());
        }

        public static float doBoundedEDwP(Trajectory traj1, AABB aabb1, Trajectory traj2, AABB aabb2, bool average=false)
        {
            // if the two trajectories aren't bounded, do a shitty difference check instead.
            if(AABB.Intersects(aabb1, aabb2))
                return doEDwP(traj1, traj2, average);
            if (average)
                return AABB.ReplacementDistance(aabb1, aabb2);
            return AABB.ReplacementDistance(aabb1, aabb2) * AABB.Coverage(aabb1, aabb2);
        }

        public static float doEDwP(Trajectory traj1, Trajectory traj2, bool average = false)
        {
            if (traj1 == null || traj2 == null)
                return float.PositiveInfinity;
            bool traj1zero = traj1.Count == 0;
            bool traj2zero = traj2.Count == 0;
            if (traj1zero && traj2zero)
                return 0;
            if (traj1zero || traj2zero)
                return float.PositiveInfinity;
            float score1 = doEDwP(traj1.rest(), traj2.rest(), average);
            // don't calculate coverage if infinity, no point
            if (!float.IsInfinity(score1))
                score1 += traj1.replace(traj2) * traj1.coverage(traj2);
            // short-circuit
            if (score1 == 0)
                return 0;
            float score2 = doEDwP_postinsert(traj1.insert(traj2), traj2, average);
            if (score2 == 0)
                return 0;
            float score3 = doEDwP_postinsert(traj1, traj2.insert(traj1), average);
            if (score3 == 0)
                return 0;
            score1 = Math.Min(Math.Min(score1, score2), score3);
            if (average)
                return averager(traj1, traj2, score1);
            return score1;
        }

        public static float doEDwP_postinsert(Trajectory traj1, Trajectory traj2, bool average = false)
        {
            if (traj1 == null || traj2 == null)
                return float.PositiveInfinity;
            bool traj1zero = traj1.Count == 0;
            bool traj2zero = traj2.Count == 0;
            if (traj1zero && traj2zero)
                return 0;
            if (traj1zero || traj2zero)
                return float.PositiveInfinity;
            float score1 = doEDwP(traj1.rest(), traj2.rest(), average);
            // don't calculate coverage if infinity, no point
            if (!float.IsInfinity(score1))
                score1 += traj1.replace(traj2) * traj1.coverage(traj2);
            if (average)
                return averager(traj1, traj2, score1);
            return score1;
        }
    }
}
