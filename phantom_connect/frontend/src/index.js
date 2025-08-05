// src/index.js
import React, { useEffect } from "react";
import ReactDOM from "react-dom";

const App = () => {
  useEffect(() => {
    const connectPhantom = async () => {
      if (window?.solana?.isPhantom) {
        try {
          const resp = await window.solana.connect();
          const walletAddress = resp.publicKey.toString();
          window.parent.postMessage({ wallet: walletAddress }, "*");
        } catch (err) {
          window.parent.postMessage({ wallet: null }, "*");
        }
      } else {
        window.parent.postMessage({ wallet: null }, "*");
      }
    };

    connectPhantom();
  }, []);

  return <div>Connecting to Phantom...</div>;
};

ReactDOM.render(<App />, document.getElementById("root"));
