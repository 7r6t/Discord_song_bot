{
  description = "Discord Music Bot";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          python311
          ffmpeg
          python311Packages.discordpy
          python311Packages.yt-dlp
          python311Packages.pynacl
          python311Packages.python-dotenv
        ];
      };
    };
}
