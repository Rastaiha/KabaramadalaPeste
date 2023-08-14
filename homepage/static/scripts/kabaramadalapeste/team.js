var jitsi = document.getElementById('jitsi');

var api;

const jitsiCofgi = {
  roomName: jitsi.dataset.uuid,
  parentNode: jitsi,
  width: '100%',
  height: '300px',
  configOverwrite: {
    disableDeepLinking: true,
    prejoinPageEnabled: false,
    startAudioOnly: false,
    startWithVideoMuted: true,
  },
  interfaceConfigOverwrite: {
    SHOW_CHROME_EXTENSION_BANNER: false,
    RECENT_LIST_ENABLED: false,
    VIDEO_QUALITY_LABEL_DISABLED: true,
    CONNECTION_INDICATOR_DISABLED: true,
    TOOLBAR_ALWAYS_VISIBLE: true,
    DEFAULT_BACKGROUND: '#eaeaea',
    HIDE_INVITE_MORE_HEADER: true,
    DISPLAY_WELCOME_PAGE_CONTENT: false,
    GENERATE_ROOMNAMES_ON_WELCOME_PAGE: false,
    SHOW_JITSI_WATERMARK: false,
    APP_NAME: 'Rasta Meet',
    NATIVE_APP_NAME: 'Rasta Meet',
    MOBILE_APP_PROMO: false,
    PROVIDER_NAME: 'Rasta',
    TOOLBAR_BUTTONS: [
      'microphone', 'camera', 'closedcaptions', 'desktop', 'embedmeeting', 'fullscreen',
      'fodeviceselection', 'profile', 'chat', 'recording',
      'livestreaming', 'etherpad', 'sharedvideo', 'settings', 'raisehand',
      'videoquality', 'filmstrip', 'invite', 'feedback', 'stats', 'shortcuts',
      'tileview', 'videobackgroundblur', 'download', 'help', 'mute-everyone', 'security'
  ],
  },
};
api = new JitsiMeetExternalAPI('meet.jit.si/r/', jitsiCofgi);
