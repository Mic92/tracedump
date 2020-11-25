{ stdenv
, buildImage
, runCommand
, iana-etc
, mysql
, mysqlDatadir
, callPackage
}:
buildImage {
  pkg = callPackage ./dummy.nix {};
  extraFiles = {
    "file".path = runCommand "file" {} ''
      yes "a" | head -c ${toString 3145728} > $out || true
    '';

    "fio-rand-RW-smp-1.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=1
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';
    "fio-rand-RW-smp-2.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=2
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';
    "fio-rand-RW-smp-4.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=4
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';
    "fio-rand-RW-smp-6.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=6
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';
    "fio-rand-RW-smp-8.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=8
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';

    "nginx/proxy/.keep" = "";
    "nginx/scgi/.keep" = "";
    "nginx/uwsgi/.keep" = "";
    "nginx/client_body/.keep" = "";
    "nginx/fastcgi/.keep" = "";
    "nginx/nginx.conf" = ''
      master_process off;
      daemon off;
      error_log stderr;
      events {}
      http {
        access_log off;
        aio threads;
        server {
          listen 9000 ssl;
          default_type text/plain;
          location / {
            return 200 "$remote_addr\n";
          }
          location /test {
            alias /proc/self/cwd;
          }
          ssl_certificate /proc/self/cwd/server.cert;
          ssl_certificate_key /proc/self/cwd/server.key;
        }
      }
    '';

    "fio-rand-RW.job" = ''
      [global]
      name=fio-rand-RW
      filename=fio-rand-RW
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=1
      numjobs=8
      time_based=1
      runtime=50
      thread

      [file1]
      size=1G
      iodepth=16
    '';


    "fio-seq-RW.job" = ''
      [global]
      name=fio-seq-RW
      filename=fio-seq-RW
      rw=rw
      rwmixread=60
      rwmixwrite=40
      bs=256K
      direct=0
      numjobs=4
      time_based=1
      runtime=300
      thread

      [file1]
      size=10G
      iodepth=16
    '';
    "fio-rand-read.job" = ''
      [global]
      name=fio-rand-read
      filename=fio-rand-read
      rw=randrw
      rwmixread=60
      rwmixwrite=40
      bs=4K
      direct=0
      numjobs=4
      time_based=1
      runtime=900
      thread

      [file1]
      size=1G
      iodepth=16
    '';
    "fio-rand-write.job" = ''
      [global]
      name=fio-rand-write
      filename=fio-rand-write
      rw=randwrite
      bs=4K
      direct=0
      numjobs=4
      time_based=1
      runtime=10

      [file1]
      size=1G
      iodepth=16
    '';
    "/etc/my.cnf" = ''
      [mysqld]
      user=root
      datadir=${mysqlDatadir}
      ssl_ca=/proc/self/cwd/ca.crt
      ssl_cert=/proc/self/cwd/server.cert
      ssl_key=/proc/self/cwd/server.key
    '';
    "/etc/resolv.conf" = "";
    "/etc/services" = "${iana-etc}/etc/services";
    "/var/lib/mysql/.keep" = "";
    "/run/mysqld/.keep" = "";
    "ca.crt" = ''
      -----BEGIN CERTIFICATE-----
      MIIFSzCCAzOgAwIBAgIUTTjiHw91/2jDz9VhjyyAfIeEpsMwDQYJKoZIhvcNAQEL
      BQAwNTETMBEGA1UECgwKUmVkaXMgVGVzdDEeMBwGA1UEAwwVQ2VydGlmaWNhdGUg
      QXV0aG9yaXR5MB4XDTIwMDkyMzIzMjYwN1oXDTMwMDkyMTIzMjYwN1owNTETMBEG
      A1UECgwKUmVkaXMgVGVzdDEeMBwGA1UEAwwVQ2VydGlmaWNhdGUgQXV0aG9yaXR5
      MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAp8gLq+6CIQjZayoc2Ppo
      Z0n7MEgvUj0CSXwJjFB2pR6kLIQ+jYNnFYT8+XLzYGXDBsAgG52TjPjvL/aNjZer
      rkFANvjswkyI5fEEgl2UGmpHgnCI1Dt9cd6WuyfI7PNC/iZ6HNRnwR8qwUU4jfFE
      oWxuZWvnzTcqSyA7wykSP3Z8KMXV7fiT4+8RaBl/pFmUg4ETHJGP/8uFCYdF20vc
      HRAa6u/XlFTvwkntkhe43OmgyD73Q2Av2et5yDbxLkUddJ4xscp89eqGzXufnFUY
      HdTsewVOE1uFEVww4HPbbURFnTUHksVXBS8/k3cJKlRxgseGRieLiRWbAZMYUmiv
      otx8GsunBAp2sIs4lV4wcdVtP5nbzL5vIJ8fSR0h6zVOfWBDDoXCJAn14QQpqJwB
      320brk/GmxVOkm6x9jVlncM/OsbKdmKqyhiWbuh6j1ePL/AibdAi5MYa7ehT0gUf
      u2e7oEF2bi+B0zoIJcDKwaJJUzkE1X5iZ2obI2MnzuYj7CfEdAu5D+J9QHxF08Co
      zcymAwozpfwjZELWtRTI6lb4bUXDR6pNGlz00oCbLKBIbKJFQzNVQHUptUcTAgZc
      tYyB4Vbwdw0lPz+/Ze/tiMq7tQ7805O1Mpiu09VT06q44jcQxdIEWrZRvVgkQTPH
      156rUlY9N/b4+ap7fYswYg0CAwEAAaNTMFEwHQYDVR0OBBYEFNlbymXQ3uVk2w5e
      nruucGsAhramMB8GA1UdIwQYMBaAFNlbymXQ3uVk2w5enruucGsAhramMA8GA1Ud
      EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggIBAIhfxVLKj9z1unlCQmakggek
      O5RJn3M1gewKXeO6mXgxotP22hHdrC2c6F5kEhcV2AnR6h/BnIk8xvkQ9lc1B+Su
      yfsuyBHIKDjYfIMSZu863T3fVGWd/j96mQQepKJu11TnS6zznjBVGZVX9qQvbOJa
      oOsCiEQnQn6YyUnDqAeBXIUpyqTDRLWlfnj/EXwWphh2kMil1INGq5KOGQ606RBm
      hGjtEamN1kjs91ifE8K7+rgjPg4Y4yxq9antl2k8x9rhQAf+wmPNpQEjlTe6JInR
      qRhLYd8Xg9l+/YVPIDZQWt3BwwmpSCywsjTsykcXazwe16RIGaFoNWZvs83lNhbf
      keHg5z7Q4xKEPYbfNClqgXm0XFXWEzCbgElwFwB1+1TxYUHDKn6K9dmOPpvTQCZS
      3arY248cPRVs4lJBFz+ns/9YWEpzXACV75t8XZVMzQMblRz2wYn8POf4WFqewJab
      SrF1YaPXFiLhLCXsK+0z1H6NKJWvOR3aYad9zjCQtT/EaeK9sHlEyIByZnuOaTz4
      6oBng2nYgP8pL6ePtjqO8Bw8A3c9XVJlpXnrZ5zvS7/FslKQ0MVLPVidSYjTc4bA
      YsEJZh+7Gy3uanvuUw9WtYo9jxOlIsXlSR8IicR/nZMD1C80QBZTmIlMA0+zGyD5
      ZWC5MbmhsTnlWuvgyzEe
      -----END CERTIFICATE-----
    '';
    "ca.key" = ''
      -----BEGIN RSA PRIVATE KEY-----
      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
      -----END RSA PRIVATE KEY-----
    '';
    "server.cert" = ''
      -----BEGIN CERTIFICATE-----
      MIID4jCCAcoCFGziemq0L6SQstU9x9gmgT88MksNMA0GCSqGSIb3DQEBCwUAMDUx
      EzARBgNVBAoMClJlZGlzIFRlc3QxHjAcBgNVBAMMFUNlcnRpZmljYXRlIEF1dGhv
      cml0eTAeFw0yMDA5MjMyMzI2MDdaFw0yMTA5MjMyMzI2MDdaMCYxEzARBgNVBAoM
      ClJlZGlzIFRlc3QxDzANBgNVBAMMBlNlcnZlcjCCASIwDQYJKoZIhvcNAQEBBQAD
      ggEPADCCAQoCggEBALRiAdp8neSRW7g2PCaEfC9JokjMT5Fy/nvmLPCWJw8E3k8s
      S4TiPBDM92sQofZmZpCssLLovmEpiwwFc0R0Di1490U5tjXDJ0MOODDoJVmxi58t
      T+gfTwEssSJqrascLi6UtQeo01zw3o3cwozNx/cGj8qI9KJnpcSvftriEM9OsM8/
      oJ8E1DpccLWfkiB6Qg9jktepKdC6COmeQnI+L4FZNm6orDAmXtwaFjQTXLVqUV3+
      Nm2EH8JmykUkqU7IFURGplQyj4mmmndvILktvsfGnZmnTADkCmg2DIUB6Ud2HWpS
      Kh/uOpkxyp3HIZAbCkdH/Glsg7yDji9Oogjas10CAwEAATANBgkqhkiG9w0BAQsF
      AAOCAgEAnB4E9NEmxp2BWGU1s+uBZjst4LU8lDTRw5HPfNwIcKseouNVQNxLDJ2f
      kNvHfYrSAt0yISAgrmmRDkoTRDVzYZbjLMLhtNas5BqDPySKwkUarqhN0stduzGj
      XUnChp5KhN3Tk+rS45ZD46u78IARx/GepkmZGBd3wX+MQb8rTsgpJdLsql8LZkjd
      BJAl6mmJ7XPk+KjH6/plP7BrKaeCxEWL1osJ8vL9r960GJWldf/DryuDVKFemqAv
      1gurTmb1MVPnm1gVQXEej5W8cQEOxQL0lB7GStYxD5M0RSSHnRIZOiU+TRLHg00/
      QGitwhoq4WFX0HGU4XPmF8LfmeULN7I+lUNaPwxNWmsAbEXS9LIFvEtQ47ssfSmp
      5msKPEKRnLq5a0R46F5cYbwxcOVM+II12zUSLLG5FzF7IP3HEMv1V8H6EcTm+UzP
      OK76JYxgPR5T4Umjr8LvXMYYbtova6+WyrBAUktcYCMGOJa9m3W1+DSnHL/TfRp6
      gAdyBO9uTrEqzxdRH7Li/oTv9WoMg1w0UhAPRhvA8Ub2RzZ4+GI5c2acyQ+ViJjk
      VAXdwKVi0wPIuzRu19LTNvRkBoWvnChpRsrwpg35S6RJTLUWSup8o68FEVzul1m2
      zFP13dNTqssq6yLMst9PTJZsb7UObGRaLgHNQSdQnAFtM2FF6Cs=
      -----END CERTIFICATE-----
    '';
    "server.key" = ''
      -----BEGIN RSA PRIVATE KEY-----
      MIIEowIBAAKCAQEAtGIB2nyd5JFbuDY8JoR8L0miSMxPkXL+e+Ys8JYnDwTeTyxL
      hOI8EMz3axCh9mZmkKywsui+YSmLDAVzRHQOLXj3RTm2NcMnQw44MOglWbGLny1P
      6B9PASyxImqtqxwuLpS1B6jTXPDejdzCjM3H9waPyoj0omelxK9+2uIQz06wzz+g
      nwTUOlxwtZ+SIHpCD2OS16kp0LoI6Z5Ccj4vgVk2bqisMCZe3BoWNBNctWpRXf42
      bYQfwmbKRSSpTsgVREamVDKPiaaad28guS2+x8admadMAOQKaDYMhQHpR3YdalIq
      H+46mTHKncchkBsKR0f8aWyDvIOOL06iCNqzXQIDAQABAoIBAFmnQJ6UQ3HAIWMc
      aacHQCXMpkEicwWqrvtrurhVGNKpK8kUDfDc9New1+Q53xX1bVLI0gYKEd1+5WIz
      L0g9mnJVZijc90gfV9tHLPx51V6QFQInZkjLjtvZl6ywcuLR3c4/EP7elTbjbOn7
      aCLNgG6xrzQN//DcLRLl2tn1dD9kWnG7WQPjWOol6s0IrqYHEdSvE/TjTVRxtrkX
      YrSosDoVqXt6pg3ZZPEUbu+OaCP+H6sSysP7YFDEloCqyFdUnzKcqdT+F9IowVax
      Q9E1mgfBrNUHBl/b7exeqCY7/EHQIzy2NgG4EO7/rA8LMjo8B4h33m5JpwR4KCrO
      7ei4ua0CgYEA2ZNwLwz/MQbBmIf1IxPA34HRLPFyx6aWkLTsNIaTLuEcCyh0o+Ov
      qn8MLhERywynM3nMSC8CUlUtwJl+IqXl9txW5VJGSbVRb2oPzmDgAY2H+SHsy/Jg
      GT6+B1XHIKb2kcmLc+Uh5TB7hd/hR0Ms90bJTWzjvVyiwKBfHhz8TXcCgYEA1D0T
      yjKRfqjx8PeG/bCbnXvXkf92VSbSVEJSmOdPk5KOjB1zsDVEeECHs6cSE2miasDl
      O7j+HjgELJhYi9iO0nPCCnqKLMGhhmGccnJCcYo5Es5q2emjJyUcOEtPSuNYmDA2
      VNaRfnchBUHANmpmdNyVK3HTS0ofT4L7HCZ6assCgYALMP1FPkrmD63nlZ6zVjHG
      jVvgDu9Te6sk+Flp/j4V3DhgDo2pXG3NvEk5GWGr6xOynyI12E0rRPxcesi1KYlh
      oEXL9+ZrpirxKyhy+iKrkccbtnYCq43r3oFRyUS71jq6lv5YUMHkkxDXewOQcdEf
      SwHRvLceJ2SrudQKrX0A0wKBgBu7734YpZKbmSIX9nfoQC2QJVdavqfZ7to74HdC
      os9x81az8o4wJ8ZfCFydlGsc/rBcjJgFUI+6WjFJpyh/IAq4Pb8IzE2U7/qTftIl
      xDD6EwM2Hhhjw4I2Az4H+VCb7NPWWQM1FsYj4xjAwtFZjhHvUT7gHPBVu0m0oAPJ
      s22JAoGBAMolOEJvuta3lQ1AO3CCyC46tOXu4Ziq96+6niObelGQ4doQb6dB6Bcn
      25YXQd1Mkk8/qBcTHxSGxjlWiBef78TE19JR21I5OTPvpzaSG8S3ShiKXGbpPQck
      wKqPiYefGGLeYznTN3wq/u7HoBbH4jQHPH3B+yat6FWtq1rfDkZy
      -----END RSA PRIVATE KEY-----
    '';
    "server.dh" = ''
      -----BEGIN DH PARAMETERS-----
      MIIBCAKCAQEApzZ6pzT1vIE6+SEPDzSpp5RgVsfz0Ra5mh9WJ6MKpPn67rVPDz4t
      Og8jRRgToFKfpXgrVjVrdJ0FhSxiBIbPAEeJzb/v8U0zpIGjhTAvuwFoEooC7SzO
      7XdE/XImxe3aTbr+9bKYOD8ga1omsTRYBdACx6tTBNZPqnW9salbTr++/Ro82o12
      ReIGpdbWUTl+7cqjgwicHoIG8pnPPySb8JLJS2aj/JhXTwufht+TF+vvaBLEpyL8
      W8ShJGvvj5XKcmV3qAKzpiGRHQ9CO3jy33gtdhvxrCOitl7u/V4kaAbK/NNq082k
      37xXwyYg3/CbwnzMR+j1xaANLohOD+yzUwIBAg==
      -----END DH PARAMETERS-----
    '';
  };
  extraCommands = ''
    export USER=$(whoami)
    ${mysql}/bin/mysql_install_db --datadir=$(readlink -f root/${mysqlDatadir}) --basedir=${mysql} --auth-root-authentication-method=socket --auth-root-socket-user=$USER
    ${mysql}/bin/mysqld_safe --datadir=$(readlink -f root/${mysqlDatadir}) --socket=$TMPDIR/mysql.sock &
    while [[ ! -e $TMPDIR/mysql.sock ]]; do
      sleep 1
    done
    ${mysql}/bin/mysql -u $USER --socket=$TMPDIR/mysql.sock <<EOF
    GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;
    CREATE DATABASE root;
    FLUSH PRIVILEGES;
    EOF
  '';
}
