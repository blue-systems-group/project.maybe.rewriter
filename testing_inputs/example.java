// 27 Feb 2015 : GWA : Testing comments about the package statement.

/* 27 Feb 2015 : GWA : Here's another one. */

package testing_inputs.maybe;

// 26 Feb 2015 : GWA : These should work.

int i = maybe("simple test") 1, 2;
public String test = maybe("another test") "one","two",   "three";

// 26 Feb 2015 : GWA : These should fail because they are inside comments or
// strings.

/* private bool fail = maybe("not_match") true, false */
// private bool anotherFail = maybe("please_no") true, false
public String test = "maybe (\"again_no\") true, false";

// 26 Feb 2015 : GWA : I guess Java doesn't like single-quoted strings? Who
// knew!

private String another_test = 'maybe (\'please_no\') true, false';

maybe ("block test") {
  if ("true") {
    i = 0;
  } else {
    j = 0;
    maybe ("third block test") {
      i = 1;
    } or {
      j = 2;
    } or {
      j = 3;
    }
  }
} or {
  i = 1;
} or {
  j = 2;
  maybe ("another block test") {
    j = 3;
  }
}

// 5 Mar 2015 : JAA : Modified previous example to consider 'or'
// blocks on a newline
maybe ("newline_or block test") {
  if ("true") {
    i = 0;
  } else {
    j = 0;
    maybe ("newline_or third block test") {
      i = 1;
    } 
		or {
      j = 2;
    } 
		or {
      j = 3;
    }
  }
} 
or {
  i = 1;
} 
or {
  j = 2;
  maybe ("newline_or another block test") {
    j = 3;
  }
}
