using System;

namespace Sest.UiFixes
{
    static class StutterPolicyTests
    {
        static int checks;
        static void Check(bool b, string why) { checks++; if (!b) throw new Exception(why); }
        static void Main()
        {
            var batch = new CleanupBatchGate();
            Check(batch.Take(100) == 0, "Idle must never sweep");
            for (int i = 0; i < 4; i++) batch.Request(1 + i * 0.01f);
            Check(batch.Take(1.2f) == 0, "Wait for texture build burst to finish");
            Check(batch.Take(1.4f) == 4, "Four native terrain requests must yield one queued sweep");
            Check(batch.Take(1.5f) == 0 && batch.Pending == 0, "Do not repeat an already consumed sweep");
            batch.Request(3);
            for (int i = 1; i <= 10; i++) batch.Request(3 + i * 0.19f);
            Check(batch.Take(5.01f) == 11, "Continuous requests must not postpone cleanup past two seconds");
            batch.Request(7); batch.Clear();
            Check(batch.Take(100) == 0, "Native scene cleanup owns teardown; discard queued mission work");
            batch.Request(101);
            Check(batch.Take(101.2f) == 0 && batch.Take(101.5f) == 1, "A new mission must get a fresh quiet period");

            var frames = new FrameWindow();
            foreach (double invalid in new[] { 0, -1, double.NaN, double.PositiveInfinity }) frames.Add(invalid);
            Check(frames.Count == 0, "Ignore invalid frame samples");
            for (int i = 0; i < 60; i++) frames.Add(1.0 / 60);
            Check(frames.Count == 60 && Math.Abs(frames.Seconds - 1) < 0.00001 && frames.P95Ms == 17, "A 60 Hz frame sequence must describe 60 fps");
            frames.Clear();
            for (int i = 0; i < 95; i++) frames.Add(1.0 / 60);
            for (int i = 0; i < 5; i++) frames.Add(0.21);
            Check(frames.P95Ms == 17 && frames.Over50 == 5 && frames.MaxMs == 210, "Isolated cleanup stalls must remain visible independently of p95");
            frames.Clear(); frames.Add(4);
            Check(frames.P95Ms == 1000 && frames.MaxMs == 4000, "Histogram overflow must retain the real maximum");
            frames.Clear();
            Check(frames.Count == 0 && frames.P95Ms == 0 && frames.Seconds == 0 && frames.MaxMs == 0, "Reset at mission/report boundaries");
            Console.WriteLine("Terrain cleanup/frame pacing checks passed: " + checks);
        }
    }
}
