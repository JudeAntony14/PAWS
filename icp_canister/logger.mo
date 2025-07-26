// Motoko canister for basic logging
import Array "mo:base/Array";

actor Logger {
  var logs : [Text] = [];

  public func record(message : Text) : async () {
    logs := Array.append(logs, [message]);
  };

  public query func view() : async [Text] {
    logs
  };
} 