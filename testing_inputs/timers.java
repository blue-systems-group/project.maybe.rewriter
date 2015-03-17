return PendingIntent.getActivityAsUser(context, 0, intent, 0, null, UserHandle.CURRENT);
private ScheduledThreadPoolExecutor mWakeExecutor = new ScheduledThreadPoolExecutor(1);
signal.await(10, TimeUnit.SECONDS);
mAlarmManager = (AlarmManager)mContext.getSystemService(Context.ALARM_SERVICE);
private static final int NO_FIX_TIMEOUT = 60 * 1000;
private static final int GPS_POLLING_THRESHOLD_INTERVAL = 10 * 1000;
