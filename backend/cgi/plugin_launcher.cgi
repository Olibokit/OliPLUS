#!/usr/bin/perl

use Modern::Perl;
use CGI      qw( -utf8 );
use C4::Auth qw( check_cookie_auth );

use FrameworkPlugin;

my $input = CGI->new;

my ($auth_status) = check_cookie_auth(
    $input->cookie('CGISESSID'),
    { catalogue => 1 }
);

if ( $auth_status ne "ok" ) {
    print $input->header( -type => 'text/plain', -status => '403 Forbidden' );
    exit 0;
}

my $plugin_name = $input->param("plugin_name") // '';
$plugin_name =~ s/[^\w\-]//g;  # Sanitize input

unless ($plugin_name) {
    print $input->header( -type => 'text/plain', -status => '400 Bad Request' );
    print "Missing plugin_name parameter.";
    exit 0;
}

my $plugin = FrameworkPlugin->new({ name => $plugin_name });
$plugin->launch({ cgi => $input });
