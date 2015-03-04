// 3 Mar 2015 : JAA : Just a bunch of random if-else blocks along with
// content interspersed between them.

System.out.println("Some random text");
boolean user = true;
if (user) {
  System.out.println("Hello user");
} else {
  System.out.println("Hello stranger");
  int x = 1000;
}

// 3 Mar 2015: JAA : Enhancement of the above statement. If-else-if statement
// also need to be parsed.
System.out.println("Another set of random texts");
int value = 4;
if (value == 1) {
  System.out.println("I have a value of one.");
} else if (value == 2) {
  System.out.println("I have a value of two.");
} else if (value == 3) {
  System.out.println("I have a value of three.");
} else {
  System.out.println("I have a value of four.");
}

// 3 Mar 2015: JAA : Also need to parse nested if-else statements.
System.out.println("Some random text.");
int x = 100;
if (x < 50) {
  System.out.println("I'm less than 50");
  if (x < 25) {
    System.out.println("I'm less than 25");
  } else {
    System.out.println("I'm greater than 25 but less than 50");
  }
} else {
  System.out.println("I'm greater than or equal to 50");
  if (x < 75) {
    System.out.println("I'm less than 75 but greater than 50");
  } else {
    System.out.println("I'm greater than 75");
  }
}

 3 Mar 2015: JAA : Trying an actual piece of code in AOSP. 
 File name: ClipData.java
if (uri != null) {

    // First see if the URI can be opened as a plain text stream
    // (of any sub-type).  If so, this is the best textual
    // representation for it.
    FileInputStream stream = null;
    try {
        // Ask for a stream of the desired type.
        AssetFileDescriptor descr = context.getContentResolver()
                .openTypedAssetFileDescriptor(uri, "text/*", null);
        stream = descr.createInputStream();
        InputStreamReader reader = new InputStreamReader(stream, "UTF-8");

        // Got it...  copy the stream into a local string and return it.
        StringBuilder builder = new StringBuilder(128);
        char[] buffer = new char[8192];
        int len;
        while ((len=reader.read(buffer)) > 0) {
            builder.append(buffer, 0, len);
        }
        return builder.toString();

    } catch (FileNotFoundException e) {
        // Unable to open content URI as text...  not really an
        // error, just something to ignore.

    } catch (IOException e) {
        // Something bad has happened.
        Log.w("ClippedData", "Failure loading text", e);
        return e.toString();

    } finally {
        if (stream != null) {
            try {
                stream.close();
            } catch (IOException e) {
            }
        }
    }

    // If we couldn't open the URI as a stream, then the URI itself
    // probably serves fairly well as a textual representation.
    return uri.toString();
}

// 3 Mar 2015: JAA : Trying to parse an exceptionally long expression as 
// the condition.
System.out.println("Do something");
int x = 1000, y =50;
boolean z = true;
if(x>20 && x<30 && y!=0 || (z=true && x>30) || (y<30 && x<10) || (x!=50 &&
		y!=20 || z=false) && (z=true && x!=0 && y!=0)) {
	System.out.println("Do something");
}
