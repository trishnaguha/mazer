import logging

import attr

from ansible_galaxy.models.repository_spec import RepositorySpec

log = logging.getLogger(__name__)

EXAMPLE = '''
# from galaxy
- src: yatesr.timezone

# from GitHub
- src: https://github.com/bennojoy/nginx

# from GitHub, overriding the name and specifying a specific tag
- src: https://github.com/bennojoy/nginx
  version: master
  name: nginx_role

# from a webserver, where the role is packaged in a tar.gz
# - src: https://some.webserver.example.com/files/master.tar.gz
#  name: http-role

# from Bitbucket
# - src: git+https://bitbucket.org/willthames/git-ansible-galaxy
#  version: v1.4

# from Bitbucket, alternative syntax and caveats
# - src: https://bitbucket.org/willthames/hg-ansible-galaxy
#  scm: hg

# from GitLab or other git-based scm, using git+ssh
# - src: git@gitlab.company.com:mygroup/ansible-base.git
#   scm: git
#  version: "0.1"  # quoted, so YAML doesn't parse this as a floating-point value
'''


# enum-ish, currently we only support exact match
# (and implicitly, 'any' via not setting it.
class RequirementOps(object):
    EQ = '='


class RequirementScopes(object):
    INSTALL = 'INSTALL'
    RUNTIME = 'RUNTIME'


@attr.s(frozen=True)
class Requirement(object):

    # The repo that is required. The RHS of the requirement.
    requirement_spec = attr.ib(type=RepositorySpec)

    # the 'operation' or expression type of a requirement
    # for ex, an 'exact' match of namespace, name, version
    # or possibly a 'just name'
    # or >= a repository spec
    # or possible, some semver specific expression TBD
    #   (like 'major.minor == 1.2' or 'major' == 1 and 'minor' >= 3)
    #
    # At the moment, the support operations are:
    #  - exact namespace and name and full version
    #  - exact namespace and name (no version compare)
    #
    # Unclear if 'no version compare' should be annotated in
    # the RepositorySpec (ie, version=None) or in the Requirement op
    #
    # If 'no version compare' is up to the RepositorySpec, then the op here
    # would indicate '==', '>', '>=' etc
    #
    # TODO: figure out if we should go ahead and track an 'op' for each compontent
    #       of RepositorySpec. For example:
    # repo_spec_a(namespace='mynamespace', name='myname', version='1.0.0')
    #
    # if repo_spec_a needs req_repo_spec(namespace='some_req_namespace', name='some_req', version=None)
    # that could have a namespace_op ==, a name_op ==, and a version_op any? noop? *?
    #
    # With per field ops, we could support repo_spec_a needing
    # req_repo_spec(namespace=='*', name='some_req', version='1.2.3') so any namespace could provide
    # the req. Lots of ambiquity that way though...
    #
    # For misc notes and ideas see:
    # - https://golang.github.io/dep/docs/Gopkg.toml.html#version (a semver aware syntax for version matching)
    # - https://github.com/Masterminds/semver  - go lib for semver
    # - https://medium.com/@sdboyer/so-you-want-to-write-a-package-manager-4ae9c17d9527
    # - https://en.wikipedia.org/wiki/Conflict-driven_clause_learning  SAT solver variant
    # operation? constraint? comparison? predicate? expression?
    op = attr.ib(default=RequirementOps.EQ)

    # The repo that has a requirement, can be null
    repository_spec = attr.ib(default=None, type=RepositorySpec)

    # do we need to resolve the dep at install time ('requirements') or
    # could we defer until runtime (like role dependencies)
    scope = attr.ib(default=RequirementScopes.INSTALL)

    def __str__(self):
        return '{repo_spec}->{req_spec_label}{op}{req_spec_version}'.format(repo_spec=str(self.repository_spec),
                                                                            req_spec_label=str(self.requirement_spec.label),
                                                                            op=self.op,
                                                                            req_spec_version=str(self.requirement_spec.version),
                                                                            )

    # FIXME: just for debugging
    def __repr__(self):
        return str(self)
