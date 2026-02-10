from engines.threat_cv.inference.video_source import VideoSource
from engines.threat_cv.inference.motion_detector import MotionDetector
from engines.threat_cv.inference.person_detector import PersonDetector
from engines.threat_cv.inference.tracker import SimpleTracker
from engines.threat_cv.inference.behavior_analyzer import BehaviorAnalyzer
from engines.threat_cv.inference.context_boost import ContextBooster
from engines.threat_cv.inference.threat_scorer import ThreatScorer


def main():
    video = VideoSource()
    motion = MotionDetector()
    detector = PersonDetector()
    tracker = SimpleTracker()
    behavior = BehaviorAnalyzer()
    context = ContextBooster()
    scorer = ThreatScorer()

    print("\n📹 Threat CV Engine running...\n")

    for frame in video.frames():
        motion_result = motion.process(frame)
        people = detector.process(frame)
        tracks = tracker.update(people)
        behavior_signals = behavior.update(tracks)
        context_result = context.compute(tracks, behavior_signals, is_night=False)
        threat_result = scorer.score(motion_result, behavior_signals, context_result)
        threat_score = threat_result.get("visual_threat_probability", 0.0)

        print(f"🔥 Threat Score: {round(threat_score, 2)}")


if __name__ == "__main__":
    main()
