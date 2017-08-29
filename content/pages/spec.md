Title: Specification template

Some formatting notes:

+ maximum line width is 72
+ a minimum of four lines from the last line on a page to the footer
+ two lines separate the header from the first line on a page
+ the first page break is a 59 lines
+ the second is at 115 lines
+ subsequent page breaks are at offset by 56 lines:
  + 171, 227, 283, 339, 395, 451, 507, 563, 619, 675, 731, 787, 843,
    899, 955, 1011, 1067, 1123, 1179, 1235, etc...

```

System Specification                                             K. Isom
system-id revision 1                                      2017 August 28


                           A new systems tool


Abstract

   This document serves as a template for describing a new systems
   tool. The abstract should be one or two sentences describing what
   it is that the system does.

Status of the Project

   The status section describes the implementation status. What features
   have been built? What work remains to be done? This should only
   describe milestone status.

Table of contents

   1. Background  . . . . . . . . . . . . . . . . . . . . . . . . .   1
   2. Characteristics . . . . . . . . . . . . . . . . . . . . . . .   1
     2.1 Key features . . . . . . . . . . . . . . . . . . . . . . .   1
     2.2 Performance constraints  . . . . . . . . . . . . . . . . .   2
     2.3 Environment  . . . . . . . . . . . . . . . . . . . . . . .   2
     2.4 Acceptance critera . . . . . . . . . . . . . . . . . . . .   2
   3. System overview . . . . . . . . . . . . . . . . . . . . . . .   2
   4. Failure modes . . . . . . . . . . . . . . . . . . . . . . . .   2
   5. Implementation  . . . . . . . . . . . . . . . . . . . . . . .   2
   6. References  . . . . . . . . . . . . . . . . . . . . . . . . .   3


1. Background

   The background should inform readers what the problem motivating this
   tool is. For educational projects, it should describe the skills that
   it should help build; for production projects, it should describe the
   nature of the problem.

2. Characteristics

   The characteristics section describes what the finished project
   should look like, including performance requirements.

2.1 Key features

   Key features are a top-level, user-view of what the system will
   provide.






K. Isom                   System Specification                  [Page 1]

system-id                  A new systems tool                August 2017


2.2 Performance constraints

   Performance constraints describe an expectation for how the system
   will perform; this includes memory usage, requests per second,
   storage constraints, connectivity requirements, and so forth.

2.3 Environment

   No system is expected to be perfectly generic; the environment
   section describes the expected usage scenarios.

2.4 Acceptance critera

   The acceptance critera are the standards by which is system will be
   judged. These critera are self-selecting, and should be represent-
   ative of a finished solution.

3. System overview

   The system overview includes a listing of all of the components, a
   high level overview of the implementation of the system, and likely
   one or more diagrams. For example, this system might consist of

   o the controller monitors the system and processes command input.
   o an administrative interface receives commands from a system
     operator, proxying them to the controller and returning controller
     responses back.
   o a user interface that handles the primary interaction with end
     users.

     +-----------------+      +------------+      +----------------+
     | admin interface +------+ controller +------+ user interface |
     +-----------------+      +------------+      +----------------+

   Further subsections may be added as necessary. It also describes the
   concepts employed by the system, such as specific vocabulary and
   key algorithms and data structures.

4. Failure modes

   This section should consider how the system will fail, and what an
   appropriate response to these scenarios is.

5. Implementation

   This section may be renamed; this and any following sections up to
   the references will cover system specific details. These might
   include communications protocols, data structures, optimisations,
   and future work or directions for the future.


K. Isom                   System Specification                  [Page 2]

system-id                  A new systems tool                August 2017


6. References


   [RFC7990]  Flanagan, H. "RFC Format Framework", RFC 7990,
              DOI 10.17487/RFC7990, December 2016,
              <http://www.rfc-editor.org/info/rfc7990>.













































K. Isom                   System Specification                  [Page 3]

