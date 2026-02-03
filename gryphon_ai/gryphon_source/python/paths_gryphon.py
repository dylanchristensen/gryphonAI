from os import makedirs
from os.path import expanduser, join

# Gryphon paths
user_mp_path = expanduser("~/.gryphon")
USER_PREFERENCES_FILENAME = join(user_mp_path, "preference_settings")
PREVIOUS_SESSION_FILENAME = join(user_mp_path, "previous_session.gry")
DEFAULT_SETTINGS_FILENAME = join(user_mp_path, "default_graph_settings.stg")
SNAPSHOTS_PATH = join(user_mp_path, "snapshots")
TRACE_GENERATOR_PATH_FILENAME = join(user_mp_path, "trace_generator_path")
EXAMPLES_PATH_FILENAME = join(user_mp_path, "preloaded_examples_path")
RIGAL_SCRATCH = join(user_mp_path, "mp_gryphon_rigal_scratch")
makedirs(RIGAL_SCRATCH, exist_ok=True) # make requisite .gryphon paths
makedirs(SNAPSHOTS_PATH, exist_ok=True) # make requisite .gryphon paths
TRACE_GENERATED_OUTFILE_TG = join(RIGAL_SCRATCH,
                                     "_mp_trace_generator_output.tg")
TRACE_GENERATED_OUTFILE_GRY = join(RIGAL_SCRATCH,
                                     "_mp_trace_generator_output.gry")

