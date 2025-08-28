{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python311
    ffmpeg
    python311Packages.discordpy
    python311Packages.yt-dlp
    python311Packages.pynacl
    python311Packages.python-dotenv
  ];
}
