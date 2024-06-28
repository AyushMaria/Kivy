import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Initialize GStreamer
Gst.init(None)

# Create the GStreamer pipeline
pipeline_str = (
    "v4l2src device=/dev/video0 ! videoconvert ! "
    "capsfilter caps=video/x-raw,width=640,height=480 ! "
    "tee name=t ! queue ! videoconvert ! x264enc ! rtph264pay ! udpsink host=127.0.0.1 port=5000 "
    "t. ! queue ! videoconvert ! cairooverlay ! videoconvert ! autovideosink"
)
pipeline = Gst.parse_launch(pipeline_str)

# Start the pipeline
pipeline.set_state(Gst.State.PLAYING)

# Wait until error or EOS
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# Cleanup
pipeline.set_state(Gst.State.NULL)

