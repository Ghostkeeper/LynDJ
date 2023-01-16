1.0 - Let's Dance
----
This is the first release of LynDJ. This release has the following features:
* A graphical interface.
  * The interface has a music library from which songs can be selected.
    * The music library shows all files in a single directory.
    * There is a file browser field to change the currently shown directory.
    * The library can be sorted by any of the track metadata fields.
    * The columns of the library can be resized.
    * Keyboard navigation through the table.
    * A button to queue or dequeue tracks from the library.
    * Track metadata can be changed by right-clicking on a table cell.
  * The interface has a playlist to show the tracks to be played.
    * Each track shows the title, duration and cumulative duration until the file completes playing.
    * The comment for the track is shown when hovered.
    * Tracks are coloured by their speed (BPM) metadata.
    * Selecting tracks in the playlist causes them to be selected in the file browser too, so that all metadata can be found.
    * Tracks can be re-ordered by dragging them around.
    * The currently playing track cannot be re-ordered.
  * The interface has a player to control the currently playing track.
    * A button to start/stop playing.
    * A volume control.
    * A playback progress tracker.
    * An image showing the Fourier transform of the track, giving an indication of what musical cues are coming.
      * Fourier images are pre-generated in the background while the music is not playing.
      * The Fourier image resolution and brightness can be adjusted in the preferences.
  * The divider between the playlist and the library can be dragged to resize both components.
  * A separate window to adjust the application preferences.
* A system to store persistent preferences.
  * The window size, state and position is also saved between application runs.
* A logging system to the terminal.
* A theme system to allow changing the look-and-feel of the application.
  * The theme can be changed on the fly without restarting the application.
  * Themes can customise colours, sizes, icons/images and fonts.
  * A default theme with a style reminiscent of art-deco.
  * Images can be re-coloured into any colour for the theme using a graphical effect.
* Tracking metadata for music files.
  * The title, author, comment, BPM and duration can be obtained from the metadata in the file, interacting with other applications.
  * This metadata is stored in a database, and updated if the file is changed.
  * Tracking when a track was last played.
  * Additional fields for the age, style and energy level of a track.
* An application icon featuring a dancer on a vinyl disc.
* Audio playback via the PyAudio library.
  * The buffer size for the audio can be adjusted in the preferences.
* Volume changes are saved and repeated when playing the track again.
  * The volume changes are shown with a graph during playback.
* Silence is trimmed from the start and end of each track.
* A configurable amount of seconds of silence between each track.
* The music gradually fades out when playback is stopped.
* A system for executing tasks in the background.
  * Some background tasks can only be executed while no music is playing.
  * The progress of executing background tasks is shown with a small icon in the interface.
* A toggle between mono and stereo.
* A session end time can be set to remind the DJ when he's going over time and by how much.