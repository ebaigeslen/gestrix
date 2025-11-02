(define (problem grip-2)
  (:domain gripper)
  (:objects
    rooma roomb - room
    b1 b2 - ball
    left right - gripper
  )
  (:init
    (at-robby rooma)
    (adjacent rooma roomb)
    (adjacent roomb rooma)
    (at b1 rooma)
    (at b2 rooma)
    (free left)
    (free right)
  )
  (:goal (and (at b1 roomb) (at b2 roomb)))
)
