from typing import List

import stp

from rj_gameplay.tactic import pass_tactic, basic_seek, goalie_tactic

from rj_msgs.msg import RobotIntent

from enum import Enum, auto

import numpy as np


class State(Enum):
    INIT = auto()
    WAIT_TO_PASS = auto()
    INIT_PASS = auto()
    PASSING = auto()
    PASSING_ASSIGN_ROLES = auto()
    INIT_SHOOT = auto()


class Basic122(stp.play.Play):
    """Basic play to score goals. Set up two flank and one center handler. Pass ball as needed.
    See tick() for more details.
    """

    def __init__(self):
        super().__init__()

        self._state = State.INIT
        """
        self._seek_pts = [
            np.array((2.0, 7.0)),
            np.array((-2.0, 7.0)),
        ]
        """

    def tick(
        self,
        world_state: stp.rc.WorldState,
    ) -> List[RobotIntent]:
        """
        init: 1 ball handler, 2 seekers, 1 goalie
        when seekers make it to hardcoded pt: ball handler passes to seeker
        when pass to seeker made: seeker shoots
        """

        if self._state == State.INIT:
            self.prioritized_tactics = [
                goalie_tactic.GoalieTactic(world_state, 0),
                basic_seek.BasicSeek(world_state),
                basic_seek.BasicSeek(world_state),
            ]

            self.assign_roles(world_state)

            self._state = State.WAIT_TO_PASS
            return self.get_robot_intents(world_state)

        elif self._state == State.WAIT_TO_PASS:

            seek_1 = self.prioritized_tactics[1]
            seek_2 = self.prioritized_tactics[2]

            # TODO: is one tick delay issue?
            if seek_1.is_done(world_state) and seek_2.is_done(world_state):
                self._state = State.INIT_PASS

            return self.get_robot_intents(world_state)

        elif self._state == State.INIT_PASS:
            init_passer_cost = stp.role.cost.PickClosestToPoint(world_state.ball.pos)
            init_receiver_cost = stp.role.cost.PickClosestToPoint(world_state.field.their_goal_loc())
            self.prioritized_tactics = [
                goalie_tactic.GoalieTactic(world_state, 0),
                pass_tactic.PassTactic(
                    world_state, init_passer_cost, init_receiver_cost
                ),
            ]

            self.assign_roles(world_state)
            self._state = State.PASSING
            return self.get_robot_intents(world_state)

        elif self._state == State.PASSING:
            # TODO: this logic is fairly crucial in role assignment
            #
            # is there a way I can force this to happen as a precondition to assign_roles?
            # maybe call assign_roles() every tick but check tactic for needs_assign before assigning it
            # (this works as the method is in Play superclass)

            # pass tactic dynamically needs assign, handle here
            # (think of as an interrupt)
            for tactic in self.prioritized_tactics:
                # TODO: goalie tactic (and all tactics?) need a needs_assign
                #       build in the logic for needs_assign of pass tactic into superclass
                if tactic.needs_assign:
                    print(f"{tactic} needs assign, says basic122")
                    self._state = State.PASSING_ASSIGN_ROLES

            # when pass is complete, go shoot
            pass_tac = self.prioritized_tactics[1]
            if pass_tac.is_done(world_state):
                self._state = State.INIT_SHOOT

            return self.get_robot_intents(world_state)

        elif self._state == State.PASSING_ASSIGN_ROLES:
            # duplicate role assign from init, merge states?
            # can't bc need to know the state that it came from
            # TODO: write interrupt-handler style state in play superclass for this behavior, where self._state returns to old state
            self.assign_roles(world_state)
            self._state = State.PASSING
            return self.get_robot_intents(world_state)

        elif self._state == State.INIT_SHOOT:
            print("INIT shoot")
            pass
