LoggingConfig = dict(LOG_DIRECTORY="")

QiraConfig = dict(
    address="127.0.0.1:8080",
    exe_path="C:/Program Files/Qira/Qira",
    window_title="Qira v2.1.0",
    trampoline_selector_position=(230, 200),  # positions on a 1600x900 TN panel
    trampoline_1_position=(230, 225),
    trampoline_2_position=(230, 245),
    trampoline_12_position=(230, 260),
    trampoline_auto_position=(230, 280),
    ready_state_position=(30, 175),
    start_state_position=(30, 210),
    routine_state_position=(30, 240),
    review_state_position=(30, 280),
    nousb_state_position=(30, 130),
    diagnosis_state_position=(30, 310),
    ready_state_color=(70, 170, 110),
    start_state_color=(220, 220, 90),
    routine_state_color=(230, 90, 90),
    review_state_color=(50, 100, 200),
    nousb_state_color=(230, 90, 90),
    diagnosis_state_color=(50, 100, 200),
)


CameraConfig = dict(
    fourcc="DIVX",
    camera_index=0,
)


ServerConfig = dict(
    filename_spec="{firstname}_{lastname}_{timestamp}",
    video_container="avi",
    save_data_directory="C:/Users/Test/enhanced-trampoline/local/save",
    save_video_directory="C:/Users/Test/enhanced-trampoline/local/save/video",
    qira_data_directory="C:/Users/Test/enhanced-trampoline/local",
)
