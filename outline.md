# Ref Availability Scheduling

## Phase 1 - Greedy

### Data Structure
- Only use true availability to schedule
- No metadata

### Algorithm
Simple greedy to get solution. 

Possible greedy approaches:
- Greedy by time: schedule games with least availabile refs first
  - if theres a solution, it probably gets it
- Greedy by ref: schedule refs with fewer hours first
  - balances hours well
- Greedy by hours: get refs with less availbility first
  - doesnt fill up incompatible slots first
- Greedy by hours scheduled - hours left

### Most refined approach
- Ensure that:
  - Each time has enough refs to be fully scheduled (schedule those games first)
    - if a time is on the border or is less than, schedule all that time first
  - All refs that have less availabilty than balanced game number (total games / refs per time slot) get scheduled first (only 1 optimal answer)

- Then: Greedy by least hours scheduled (select ref with least hours scheduled so far)
  - To break ref ties, take the person with the least amount of time slots remaining (total slots available - games scheduled)
  - To break game ties, take the time with the least amount of people available to work it (# of refs LEFT that can work at that time)

### Evaluation:
Pros:
- No proof - but should always schedule as many refs as possible per hour
- Ensures balanced hours between refs
- Ensures refs with low availability get scheduled fully first
- Prioritizes refs and games with low flexibility

Cons:
- No concept of time grouping - some people work all 4 days
- No concept of game strength; tie breakers would have to be a balance of multi-objective
- No guarentee of termination
- 

### Takeaways:
- The boundary checking is good here. In the future we should
  - Do availability checking to schedule a person defaultly
  - At each step, if a time cannot be filled, schedule as many as possible at that time
  - Breaking ties by least flexible works pretty well

### For Phase 2:
- Implement a more flexible game structure
- Add more complexity (ref ratings, game league)
- Brainstorm everything that goes into scheduling
