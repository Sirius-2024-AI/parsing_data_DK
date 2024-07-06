/*
  Update-Author: Philipp Ensinger || github.com/ensingerphilipp
  Original-Author: secretdiary.ninja
  License: (CC BY-SA 4.0)
  * */
function bin2ascii(array) {
  var result = [];

  for (var i = 0; i < array.length; ++i) {
    result.push(String.fromCharCode( // hex2ascii part
      parseInt(
        ('0' + (array[i] & 0xFF).toString(16)).slice(-2), // binary2hex part
        16
      )
    ));
  }
  return result.join('');
}

function bin2hex(array, length) {
  var result = "";

  length = length || array.length;

  for (var i = 0; i < length; ++i) {
    result += ('0' + (array[i] & 0xFF).toString(16)).slice(-2);
  }
  return result;
}

setTimeout(function() {
  Java.perform(function() {
    // MessageDigest
    var messageDigest = Java.use("java.security.MessageDigest");

    // messageDigest.getInstance.overload(
    //   'java.lang.String'
    // ).implementation = function(var0) {
    //   console.log("[*] MessageDigest.getInstance called with algorithm: " +
    //               var0);
    //   return this.getInstance(var0);
    // };

    // messageDigest.getInstance.overload(
    //   'java.lang.String', 'java.lang.String'
    // ).implementation = function(var0, var1) {
    //   console.log("[*] MessageDigest.getInstance called with algorithm: " +
    //               var0 + " and provider: " + var1);
    //   return this.getInstance(var0, var1);
    // };

    // messageDigest.getInstance.overload(
    //   'java.lang.String', 'java.security.Provider'
    // ).implementation = function(var0, var1) {
    //   console.log("[*] MessageDigest.getInstance called with algorithm: " +
    //               var0 + " and provider: " + var1);
    //   return this.getInstance(var0, var1);
    // };

    messageDigest.digest.overload().implementation = function() {
      var ret = messageDigest.digest.overload().call(this);
      console.log("[*] MessageDigest.digest called using algorithm: " +
                  this.getAlgorithm() + " (" +
                  bin2hex(Java.array('byte', ret)) +
                  ")");
      return ret;
    };


    // public void update(byte[] input)
    messageDigest.update.overload("[B").implementation = function(data) {
      var ret = messageDigest.update.overload("[B").call(this, data);
      console.log("===== MessageDigest.update called with arg: " +
                  bin2hex(Java.array('byte', data)));
      return ret;
    };




    // messageDigest.digest.overload("[B").implementation = function(data) {
    //   var ret = messageDigest.digest.overload("[B").call(this, data);
    //   console.log("[*] MessageDigest.digest called using algorithm: " + this.getAlgorithm() + "\n" +
    //               "    Data: " + bin2hex(Java.array('byte', data)) + "\n" +
    //               "    Result: " + bin2hex(Java.array('byte', ret)));
    //   return ret;
    // };
  });
}, 0);
