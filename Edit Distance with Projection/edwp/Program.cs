using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using System.IO;


namespace edwp
{

    class Program
    {
        static Trajectory FromList(List<List<double>> arr)
        {
            var points = new List<stpoint>(arr.Count);
            foreach (var point in arr)
            {
                points.Add(new stpoint((float)point[0], (float)point[1], point[2]));
            }
            return new Trajectory(points);
        }

        static List<Trajectory> LoadFromFile(string filename)
        {
            var stream = File.OpenText(filename);
            var obj = JsonConvert.DeserializeObject<List<List<List<double>>>>(stream.ReadToEnd());
            var output = new List<Trajectory>();
            foreach(var rawtraj in obj)
            {
                output.Add(FromList(rawtraj));
            }
            return output;
        }

        static Random rng;

        static void Standardtest()
        {
            var trajs = LoadFromFile("trajectories.json");
            foreach (var traj in trajs)
            {
                Console.WriteLine(traj);
            }
            var values = new List<float>();
            float[] testvals = { 5.65f, 4.64f, 7.77f, 89.65f };
            values.Add(EDwP.doEDwP(trajs[0], trajs[1], true));
            values.Add(EDwP.doEDwP(trajs[1], trajs[2], true));
            values.Add(EDwP.doEDwP(trajs[0], trajs[2], true));
            values.Add(EDwP.doEDwP(trajs[3], trajs[4]));
            for (int i = 0; i < 4; i++)
            {
                Console.Write("EDwP: ");
                Console.Write(values[i]);
                Console.Write(", should be ");
                Console.WriteLine(testvals[i]);
            }
        }

        static double GetRandRange(Random r, double min, double max)
        {
            return r.NextDouble() * (max - min) + min;
        }

        static Trajectory GetRandomTraj(int n)
        {
            if (rng == null) rng = new Random();
            var points = new List<stpoint>();
            for (int i = 0; i < n; i++)
            {
                float x = (float)GetRandRange(rng, -10, 10);
                float y = (float)GetRandRange(rng, -10, 10);
                points.Add(new stpoint(x, y, i));
            }
            return new Trajectory(points);
        }

        static void testRandomTraj(int n1, int n2)
        {
            var t0 = GetRandomTraj(1);
            var t1 = GetRandomTraj(n1);
            var t2 = GetRandomTraj(n2);
            var stopwatch = new System.Diagnostics.Stopwatch();
            EDwP.doEDwP(t0, t0, true);
            stopwatch.Start();
            var score = EDwP.doEDwP(t1, t2, true);
            stopwatch.Stop();
            Console.Write("EDwP score: ");
            Console.WriteLine(score);
            Console.Write("Elapsed time: ");
            Console.WriteLine(stopwatch.Elapsed);
        }

        // read filenames and indexes from manifest
        static void outputMatrix(string manifest, string dirin, string fileout)
        {
            var stopwatch = new System.Diagnostics.Stopwatch();
            stopwatch.Start();
            var manifestfile = File.OpenText(manifest);
            var trajinfo = JsonConvert.DeserializeObject<List<string>>(manifestfile.ReadToEnd());
            var trajs = new List<Trajectory>();
            foreach (var filename in trajinfo)
            {
                trajs.AddRange(LoadFromFile(Path.Combine(dirin, filename)));
            }
            var AABBs = new List<AABB>();
            int N = trajs.Count;
            var output = new float[N,N];

            // initialize AABBs
            for (int i = 0; i < N; i++)
            {
                AABBs.Add(new AABB(trajs[i]));
            }
            stopwatch.Stop();
            Console.WriteLine("Prep time: {0}", stopwatch.Elapsed);
            stopwatch.Reset();
            stopwatch.Start();
            for (int y = 0; y < N; y++) // go row by row
            {
                for (int x = 0; x < N; x++)
                {
                    if (x == y)
                        output[x, y] = 0;
                    else if (x < y) // if on the lower side of the diagonal, just copy value
                        output[x, y] = output[y, x];
                    else
                    {
                        output[x, y] = EDwP.doEDwP(trajs[x], trajs[y], true);
                        //output[x, y] = EDwP.doBoundedEDwP(trajs[x], AABBs[x], trajs[y], AABBs[y], true);
                    }
                }
            }
            stopwatch.Stop();
            File.WriteAllText(fileout, JsonConvert.SerializeObject(output));
            Console.WriteLine("Runtime: {0}", stopwatch.Elapsed);
            Console.WriteLine("Done.");
        }

        static void Main(string[] args)
        {
            // outputMatrix("A976C7.json", "A976C7.out.json");
            outputMatrix(args[0], args[1], args[2]);
            // testRandomTraj(40, 40);
            Console.ReadKey();
        }
    }
}
