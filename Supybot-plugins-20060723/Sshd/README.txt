Insert a description of your plugin here, with any notes, etc. about using it.
 Outline
    =======
        The plugin is able to run servers in on the same host as a running
        Supybot. These servers accept SSH connections, and authenticate against
        Supybot's user registry, and additionally a list of recognized RSA
        public keys. Users are then presented with an interface chosen by
        the protocol of the server they have connected to.

    Using
    =====
        To start a server the L{start} command can be used. Alternatively if
        the registry option plugins.Sshd.<protocol>.autoSTart is set to True,
        the server will start automatically when the plugin is started.

    Commands
    ========
        Authenticated users may issue any command to the Supybot they have
        connected to. The hostmask that is generated for Ssh connected users
        is partly random, and its authentication is cleared when the user
        logs out.

        When users issue commands, they are tagged with the fromSsh tag, an
        instance of the SshUser class, which is used for replying.

    Replying
    ========
        The OutFilter checks for messages that are replies to commands issued
        over Ssh, and if they are, it intercepts them, and uses the SshUser
        instance (that has been tagged) to redirect the reply.

    Hostmasks
    =========
        Because Sshd connected users are not connected via IRC, the concept of
        a hostmask is not specifically relevant to them. On connection one is
        randomly generated, that is used for capability and user user-specific
        purposes by Suppybot for the duration of that Ssh session.

    Walls
    =====
        Walls provide a way by which anyone can send messages to Sshd
        connected users. The 'wall' command is used (help wall). This
        functionality can be used similarly to the eggdrop partyline.

    Protocols
    =========
        Currently the plugin supports the provision of 4 different protocols
        over SSH. The protocols may be run simultansously (on different ports)
        on the same running instance of Supybot. The protocols are are:
        
            1. B{shell} - A standard line based shell protocol with line editing, and
            history. This is very much like a simple version of any
            UNIX-like shell, except commands issued are passed to Supybot,
            and replies are returned to the shell.

            2 B{ui} - A user interface (still using the OpenSSH client) which is
            somewhat more friendly and pleasing to the eye.

            3. B{plain} - A very simnple line based protocol with no echoing, or line
            editing features. The stream recognises commands on receipt of
            a '\\r' (character 13) and dispatches the buffered data as a
            command.

            4. B{pyshell} - A Python interpreter shell. This is much like the Python
            Interactive Interpreter (which it uses). It is imagined that
            this will only be used for development/debugging purposes,
            and should certainly be confined to owner use.

    RSA Keys
    ========
        In order to run the Ssh server(s) you will need to provide an RSA
        public/private key pair (DSA is not currently supported). The server
        will use these keys to identify itself with clients.

        Keys can be generated by issuing the command:

        C{ssh-keygen -t rsa}

        You will be prompted for the necessary information.

    Public key authentication
    =========================
        Before attempting password authentication, the server will check the
        client's public key with a list of authorzed keys. These keys should
        be present in the keys/authorized data directory, and should be named
        as the users name.

