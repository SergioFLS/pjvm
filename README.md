# pjvm

Toy JVM written in Python made to get more familiar on how it works.

## Goals

* Easily understandable code (for me, at least)
* No external classpath (like OpenJDK, GNU Classpath, Apache Harmony) needed, the standard library must be implemented in Python itself
* No external libraries needed for the core
* Must run in CPython and PyPy3

## Non-goals

* Performance
* Full standard library implementation, I'm probably only going to implement the mininum required to get some stuff working

## Stuff that would be cool to see

* Running a J2ME (MIDP 2.0 w/ CLDC 1.1) game
* Running a Java applet game (Need For Madness, Minecraft Classic?)
* Running Kotlin JVM code compiled for Java 8
