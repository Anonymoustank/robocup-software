import single_robot_behavior
import behavior
from enum import Enum
import main
import evaluation
import constants
import role_assignment
import robocup
import skills.capture
import math


class TouchBall(single_robot_behavior.SingleRobotBehavior):

    # tunable config values
    DribbleSpeed = 0

    class State(Enum):
        course_approach = 1

    # Move back so we hit the mouth, not the side.
    AdjDist = constants.Robot.Radius

    ## TouchBall Constructor
    # useful for reflecting/bouncing moving ballls.
    def __init__(self):
        super().__init__(continuous=False)

        self.add_state(TouchBall.State.course_approach,
                       behavior.Behavior.State.running)

        self.add_transition(behavior.Behavior.State.start,
                            TouchBall.State.course_approach, lambda: True,
                            'immediately')

        self.add_transition(TouchBall.State.course_approach,
                            behavior.Behavior.State.completed,
                            lambda: self.robot.has_ball(), 'Ball got hit!')

        self.add_transition(
            TouchBall.State.course_approach, behavior.Behavior.State.failed,
            lambda: not main.ball().valid, # TODO fail properly
            'ball was lost')


    # normalized vector pointing from the ball to the point the robot should get to in course_aproach
    def approach_vector(self):
        if main.ball().vel.mag() > 0.25 \
            and self.robot.pos.dist_to(main.ball().pos) > 0.2:
            # ball's moving, get on the side it's moving towards
            return main.ball().vel.normalized()
        else:
            return (self.robot.pos - main.ball().pos).normalized()

    ## A touch is different from a capture in that we should try to keep our
    # distance from the ball if possible, and move forward to hit the ball at
    # the last minute.
    # To do this, let's move the intercept point capture found back a bit.
    #
    # In addition, lets try to keep this point stable by choosing the closest
    # point, instead of the point that we can reach in time closest to the ball
    def find_intercept_point(self, adjusted=True):
        approach_vec = self.approach_vector()

        adjFactor = robocup.Point.direction(self.robot.angle) \
                    * -TouchBall.AdjDist
        robotPos = self.robot.pos - adjFactor

        # multiply by a large enough value to cover the field.
        approach_line = robocup.Line(
            main.ball().pos,
            main.ball().pos + approach_vec * constants.Field.Length)
        pos = approach_line.nearest_point(robotPos)

        if adjusted:
            pos += adjFactor

        return pos

    def execute_course_approach(self):
        # don't hit the ball on accident
        pos = self.find_intercept_point()
        self.robot.move_to(pos)

    def role_requirements(self):
        reqs = super().role_requirements()
        reqs.require_kicking = True
        # try to be near the ball
        if main.ball().valid:
            reqs.destination_shape = main.ball().pos
        return reqs
