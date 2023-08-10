# Chess-Bot
Chess Bot I wrote to learn about minimax, tree pruning and for fun

honorable mention to [a similar, but much more advanced project](https://github.com/Stargor14/carnosaEngine) i attempted, but eventually scrapped

That one tried to recreate this project, but with a heavy focus on machine learning and evolutionary neural networks / biomimetic algorithms. It ended up being a bit too ambitious for me at the moment

## Topics: Tree Search, computer graphics, Web API

[demo of the bot beating me](https://www.youtube.com/watch?v=ltoRKf2a5g4)

![screenshoit of board](temp.png)

Chess 1 was my first attemt to create the chess board from scratch using a pandas dataframe and python classes/objects to store information about pieces

After reaching 700 lines of code and still not haveing started on what I had actually set out to do, I chose to restart using the python-chess library. This allowed me to focus on creating a capable chess bot instead of implementing the rules of chess; reinventing the wheel.
Also had some fun with the "soundtrack" I made.

Overall, I learned a ton about pygame, minimax algorithms and recursion.
I also added Lichess api functionality so that you can verse the bot online.
It ended up being better than 1100ELO but worse 1400ELO, so not half bad
