# Reserved Keywords

Certain usernames will not be allowed because they are reserved keywords that have specific meaning for SAM.
- <VOICE> indicates that the statement was spoken out-loud.
- <CON> indicates that the statement was made as part of conscious dialog.
- <SUB> indicates that the statement was made as part of subconscious dialog.

# System Notifications (Received by SAM in response to different events)

The system will be able to inject information through system notifications. Many of these notifications will be registered at the conscious level, but some may be registered at the subconscious level, if they are "background information" much the same way that people may subconsciously process background information but they might not register it consciously if they're not paying active attention.

## Notification Types

System notifications will be in language form, as SAM should be able to understand them.

- Waking Up
- User Connected
- User Disconnected
- New User Message

# System Commands (Ways for SAM to interact with the system and also beyond)

Unlike with system notifications, commands issued by SAM will have to be in a specific format.

- Help command, which will inform SAM of the different commands available if it forgets.
- Switch Active User
- Get Active User (Useful to remind AI of who they're currently speaking to)
- Send Message To User

# Parameter Tweaking

There's still a lot of testing to do to figure out which parameters seem to work the best. However, it might be useful to have dynamic parameters. Indeed, doing so can help produce various mental states, including deep focus, creative, etc.

# Issues

There are a lot of issues that I still haven't figured out.

- openai doesn't seem to include the ability to check how much of a balance is left and how much is used, through the API, only the dashboard. What is available is the ability to track how many tokens are used for a given completion, and the total usage while running can be tracked. But that doesn't let the system know how much available balance there is to work with.

# Notes

There's still a lot that I'm not sure about when it comes to learning/dreaming. One thing that might make sense is to have a separate model for chat vs internal dialog, and maybe even subconscious. That's maintaining and updating three different models though.

I also can't get async and threading to work well together. I might have to really scrap the threaded layering and partition system and replace it with a single method that goes through them. One option is rather than trying to get all subconscious partitions to fight each other, randomly select one to trigger.

One thing that may be useful is replacing the current blocking openai access calls with streaming calls, and letting user and subconscious insertions break into current thoughts. A thought is not always complete before something else happens.

Currently, information is passed between layers simply by pushing the same string to both layers. However, a translation model may eventually be needed to get the layers to cooperate with each other better.

The starved, hungry,full, gorged parameters should be flexible. 
