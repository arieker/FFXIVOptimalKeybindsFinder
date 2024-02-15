import math

'''
* General summary/README

Explanation of the problem and how it must be solved:
Assume there are 3 "hotbars" in the video game that is being played, and x number of different actions that can be bound to those buttons on the hotbar.
Each hotbar is 4x3, (horizontal x vertical) and the lower indexes are preferred for the most used buttons.
The first level of hotbar is without modifiers. The second and third are holding Shift and Ctrl respectively.
Switching between these hotbars is generally a lot easier than going across the hotbar, however, switching rapidly is extremely not good
this can be adjusted in the future so for now we just need to find a general solution with a "weight" variable for hotbar jumping.

The hotbars look like this:
[3, 6, 9, 12] [3, 6, 9, 12] [3, 6, 9, 12]
[2, 5, 8, 11] [2, 5, 8, 11] [2, 5, 8, 11]
[1, 4, 7, 10] [1, 4, 7, 10] [1, 4, 7, 10]

https://i.rtings.com/assets/products/r2LxkrXF/steelseries-aerox-9-wireless/extra-buttons-small.jpg

-1 represents an unbound button. No negative numbers are used otherwise.

! Higher level future issues with the problem that must be solved somehow in the future after a general algorithm is found !

There are mitigation buttons that are not necessarily used consistently at all, but still need fast access to be pressed even if they are not pressed
in a predictable manner, and are not used nearly as much as the other buttons.

AOE buttons exist that are only used in specific raids that require AOE combos to be performed, you could create two separate hotbar arrangements for AOE and non AOE raids
but that would be quite silly and not what we're looking for here.

Those 2 can be solved by feeding the program hundreds of raid rotations and then finding the optimal solution even though the usage of the mitigation skills is not consistent, statistically it would reach a best solution.

The far right buttons on the hotbar (12, 11, 10) can technically be pressed with the joint of your thumb meaning that the distance to them could technically always be zero this can be a flag whether you want to consider it or not.

? How will this program work?

We will take an input file of a sequence of numbers of actions pressed throughout a raid encounter. (This is called a rotation since it follows a pattern and repeats over time, see line 46)
Each number corresponds to one different "skill" and there is a key.txt for the ingame names of those actions in this repo.
We will construct the 3d array and create a function that has a cursor traverse the array and count how much distance it travels.
The cursor will traverse in the order of the sequence in the input file where each index counts as one movement distance unit.
(hotbar-hotbar traverses might be weighed more, read line 12).
We must find the most optimal way to populate the array to minimize the amount of distance the cursor must travel through its path.

Because of the structure of this problem, something like shortest path Djikstras will not work, since instead of finding the shortest distance between the points,
we are finding the shortest distance possible of PLACEMENTS of the points that will be traversed in the order we already know.
Shortest path - find shortest distance from a - b by figuring out the path
This problem - we already know the path, find the shortest distance possible when PLACING the locations.

! Non FFXIV Players Terminology Reference
Hotbar - One 3x4 array is considered a hotbar, they fit 12 actions and you can bind one action per slot on the hotbar. The same action can be bound to multiple slots if you so wish but it's generally strange to do that.
Rotation - Your rotation is a consistent sequence of actions that you will use throughout a raid. This is called a rotation because it generally repeats after a certain amount of time (generally every 2 minutes). The rotation is made up of GCDs and oGCDs, but mainly GCDs.
GCD - An action that can be used every 2.5 seconds, these are used a ton.
oGCD - An action that is on a cooldown, this can vary anywhere from 2minutes to just 15 seconds.
AOE - Area of effect. AOE GCDs and oGCDs exist, and are generally only used in AOE specific raids. (See line 25)
'''

# Weight for switching between the 3 hotbars, not for going from one point to another on a single hotbar, this is for the future
hotbar_change_weight = 0.5
#Can you press 10 11 and 12 with the joint of your thumb resulting in a distance of zero?
joint_pressing = False

# You can manually make the hotbars here but obviously the goal of the program will be to build the best ones that is the solution we are looking for
# I guess maybe in the future you can input your own hotbar here to compare how good it is vs the optimal one (solution)
hotbars = [
  [
    [2, 5, 8, 11],
    [1, 4, 7, 10],
    [0, 3, 6, 9]
  ],
  [
    [14, 17, 20, 23],
    [13, 16, 19, 22],
    [12, 15, 18, 21]
  ],
  [
    [26, 29, 32, 35],
    [25, 28, 31, 34],
    [24, 27, 30, 33]
  ]
]

# This is my personal hotbar, for testing and comparison purposes. Can be commented out. It does not include '8' because I bind that to the keyboard. Ignore for now. Can be considered later.

hotbars = [
  [
    [6, 7, 9, 12],
    [1, 4, 5, -1],
    [0, 2, 3, -1]
  ],
  [
    [10, 13, -1, -1],
    [-1, -1, -1, -1],
    [-1, -1, -1, 11]
  ],
  [
    [-1, -1, -1, -1],
    [-1, -1, -1, -1],
    [-1, -1, -1, -1]
  ]
]


# Read the rotation
with open('rotation.txt', 'r') as fo:
    rotation = [int(line.strip()) for line in fo.readlines()]

# This is from gpt I just wanted it to please print this way so its easier to visually see
def print_hotbars():
  transposed_hotbars = list(map(list, zip(*hotbars)))
  for row in transposed_hotbars:
    print(*row)

# This is for distance between two coords on the hotbars
def distance_coords(x1, y1, z1, x2, y2, z2):
  distance = math.hypot(y2 - y1, z2 - z1)
  if (x1 != x2): #hotbar switch
    distance += hotbar_change_weight
  return distance

# This is a shortcut for distance between two values on the hotbars
def distance_values(x, y):
  # Find indices of value1 and value2
  index1 = None
  index2 = None
  for i, sub_lst in enumerate(hotbars):
    for j, sub_sub_lst in enumerate(sub_lst):
      for k, item in enumerate(sub_sub_lst):
        if item == x:
          index1 = (i, j, k)
        elif item == y:
          index2 = (i, j, k)

  # Check if both values were found
  if index1 is None or index2 is None:
    return None
  
  distance = distance_coords(index1[0], index1[1], index1[2], index2[0], index2[1], index2[2])

  return distance

# Every single action that is in the rotation must be in the hotbar
def test_layout():
  total_distance = 0
  for i in range(len(rotation) - 1):
    try:
      total_distance += distance_values(rotation[i], rotation[i+1])
    except:
       print("Not all actions in the rotation have been added to the hotbar")
       return None
  return total_distance

#
# Main
#

# Find the optimal solution here

print("Rotation: %s" % rotation)
print_hotbars()
try:
  print("Final score lower is better: %0.2lf" % test_layout())
except:
  print("Final score lower is better: %s" % (test_layout()))