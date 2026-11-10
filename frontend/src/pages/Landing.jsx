import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
  School,
  GraduationCap,
  Users,
  BookOpen,
  Award,
  ShieldCheck,
  ArrowRight,
  Bell,
  Phone,
  Mail,
  MapPin,
  Calendar,
  CheckCircle2,
  Cpu,
  Sparkles,
  ExternalLink,
  ChevronRight,
  Search,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

const ACADEMIC_BRANCHES = [
  // 10 Engineering Disciplines
  {
    code: 'CIV',
    name: 'Civil Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-amber-600',
    badgeColor: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
    head: 'Dr. B. C. Udayashankar',
    intake: '60 Seats',
    labs: 'Structural Dynamics Lab, Geotechnical Eng Lab, CAD Center, Environmental Eng Lab',
    description: 'Focusing on structural mechanics, transportation networks, environmental hydraulics, green architecture, surveying, and smart urban infrastructure planning.',
  },
  {
    code: 'CSE',
    name: 'Computer Science and Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-blue-600',
    badgeColor: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    head: 'Prof. Anita Rao',
    intake: '180 Seats',
    labs: 'High-Performance GPU Cluster, Cloud Systems Lab, Cyber Security Center, Open Source Hub',
    description: 'Specializations in Machine Learning, Cloud Systems, Big Data, and Cyber Security. High-speed GPU computing infrastructure for student project development.',
  },
  {
    code: 'EEE',
    name: 'Electrical and Electronics Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-yellow-600',
    badgeColor: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    head: 'Dr. H. N. Suresh',
    intake: '60 Seats',
    labs: 'Power Electronics Lab, Electric Drives Lab, Smart Grid & Renewable Energy Center',
    description: 'Mastering electrical power generation, renewable solar/wind integration, power systems analysis, electric vehicle drives, and embedded industrial automation.',
  },
  {
    code: 'ECE',
    name: 'Electronics and Communications Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-indigo-600',
    badgeColor: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    head: 'Dr. Geetha K',
    intake: '120 Seats',
    labs: 'VLSI Chip Design Center, Advanced DSP Lab, RF & Microwave Telemetry Lab, IoT Embedded Lab',
    description: 'Advanced studies in VLSI semiconductor design, embedded microcontrollers, IoT sensor telemetry, wireless communications, and digital signal processing.',
  },
  {
    code: 'ISE',
    name: 'Information Science and Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-emerald-600',
    badgeColor: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300',
    head: 'Dr. Manjunath Swamy',
    intake: '120 Seats',
    labs: 'Enterprise Software Studio, Big Data Pipelines Lab, Modern DevOps Cloud Hub',
    description: 'Focused on enterprise software systems, data engineering pipelines, distributed networks, cloud security protocols, and modern DevOps agile delivery practices.',
  },
  {
    code: 'MECH',
    name: 'Mechanical Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-red-600',
    badgeColor: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    head: 'Dr. K. S. Sridhar',
    intake: '60 Seats',
    labs: 'Robotics & Mechatronics Lab, CNC Precision Machining Lab, Thermal Engineering Center',
    description: 'Encompassing CAD/CAM computer-aided engineering, robotics, thermal dynamics, additive 3D manufacturing, fluid mechanics, and sustainable automotive systems.',
  },
  {
    code: 'AIML',
    name: 'Artificial Intelligence and Machine Learning',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-violet-600',
    badgeColor: 'bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-300',
    head: 'Dr. Chethan K R',
    intake: '60 Seats',
    labs: 'Deep Learning Vision Lab, Generative AI Studio, Autonomous Agents Sandbox',
    description: 'Dedicated to neural networks, computer vision, natural language processing, LLMs, reinforcement learning, and ethical predictive AI system deployment.',
  },
  {
    code: 'CE',
    name: 'Computer Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-cyan-600',
    badgeColor: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/30 dark:text-cyan-300',
    head: 'Prof. Ramesh Kulkarni',
    intake: '60 Seats',
    labs: 'Hardware-Software Co-Design Lab, Real-Time Embedded Systems Lab, Edge Computing Lab',
    description: 'Bridging computer hardware architecture, low-level firmware engineering, real-time operating systems, IoT edge devices, and FPGA circuit design.',
  },
  {
    code: 'CSDS',
    name: 'Computer Science and Engineering(Data Science)',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-teal-600',
    badgeColor: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
    head: 'Dr. Pradeep N',
    intake: '60 Seats',
    labs: 'Big Data Hadoop/Spark Cluster, Business Intelligence Lab, Statistical Modeling Hub',
    description: 'Specializing in massive dataset processing, predictive analytics, statistical hypothesis testing, data visualization, ETL workflows, and quantitative modeling.',
  },
  {
    code: 'CSD',
    name: 'Computer Science and Design',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline',
    borderColor: 'border-l-purple-600',
    badgeColor: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    head: 'Dr. Vinayaka B',
    intake: '60 Seats',
    labs: 'HCI Usability Lab, AR/VR Interactive Simulation Lab, Digital Media Production Studio',
    description: 'Blending computational software engineering with human-computer interaction (HCI), UI/UX product design, interactive 3D graphics, and digital media technology.',
  },

  // 4 Basic Science and Humanities Departments
  {
    code: 'PHY',
    name: 'Physics',
    category: 'basic_science',
    categoryLabel: 'Basic Science & Humanities',
    borderColor: 'border-l-sky-600',
    badgeColor: 'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300',
    head: 'Dr. M. S. Giridhar',
    intake: 'All 1st Year Streams',
    labs: 'Engineering Physics Lab, Optics & Laser Research Lab, Nanotechnology Studio',
    description: 'Foundational and applied physics covering semiconductor physics, lasers, quantum mechanics, electromagnetism, and advanced nanotechnology materials.',
  },
  {
    code: 'MATH',
    name: 'Mathematics',
    category: 'basic_science',
    categoryLabel: 'Basic Science & Humanities',
    borderColor: 'border-l-pink-600',
    badgeColor: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
    head: 'Dr. S. K. Narayana',
    intake: 'All 1st & 2nd Year Streams',
    labs: 'Computational Mathematics Lab, Numerical Analysis Center, MATLAB & SageMath Studio',
    description: 'Providing rigorous mathematical foundations in multivariable calculus, linear algebra, discrete mathematics, complex variables, and stochastic probability modeling.',
  },
  {
    code: 'CHEM',
    name: 'Chemistry',
    category: 'basic_science',
    categoryLabel: 'Basic Science & Humanities',
    borderColor: 'border-l-lime-600',
    badgeColor: 'bg-lime-100 text-lime-800 dark:bg-lime-900/30 dark:text-lime-300',
    head: 'Dr. B. K. Shanthala',
    intake: 'All 1st Year Streams',
    labs: 'Engineering Chemistry Lab, Instrumental Analysis Center, Corrosion & Battery Research Lab',
    description: 'Engineering chemistry focusing on polymer materials, electrochemical energy storage, water purification, smart coatings, and battery cell nanotechnology.',
  },
  {
    code: 'HUM',
    name: 'Humanities',
    category: 'basic_science',
    categoryLabel: 'Basic Science & Humanities',
    borderColor: 'border-l-rose-600',
    badgeColor: 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300',
    head: 'Prof. Sandhya Rani',
    intake: 'All Undergraduate Semesters',
    labs: 'Digital Language Lab, Professional Phonetics Studio, Communication Skills Center',
    description: 'Nurturing communicative English, Samskrutika/Balake Kannada, Constitution of India, Universal Human Values, and professional engineering ethics.',
  },
];

export default function Landing() {
  const navigate = useNavigate();

  // Branch filter & search state
  const [deptTab, setDeptTab] = useState('all'); // 'all' | 'engineering' | 'basic_science'
  const [deptSearch, setDeptSearch] = useState('');

  const filteredBranches = ACADEMIC_BRANCHES.filter((b) => {
    const matchesTab =
      deptTab === 'all' ||
      (deptTab === 'engineering' && b.category === 'engineering') ||
      (deptTab === 'basic_science' && b.category === 'basic_science');
    const matchesSearch =
      deptSearch.trim() === '' ||
      b.name.toLowerCase().includes(deptSearch.toLowerCase()) ||
      b.code.toLowerCase().includes(deptSearch.toLowerCase()) ||
      b.head.toLowerCase().includes(deptSearch.toLowerCase());
    return matchesTab && matchesSearch;
  });

  // Contact form state
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    phone: '',
    subject: 'Admissions Inquiry',
    message: '',
  });

  const handleContactSubmit = (e) => {
    e.preventDefault();
    if (!contactForm.name || !contactForm.email || !contactForm.message) {
      toast.error('Please fill in all required fields.');
      return;
    }
    toast.success('Thank you! Your message has been received by the Admissions & Academic Office.');
    setContactForm({
      name: '',
      email: '',
      phone: '',
      subject: 'Admissions Inquiry',
      message: '',
    });
  };

  return (
    <div className="min-h-screen bg-page text-ink dark:bg-dark-page dark:text-dark-text flex flex-col font-body">
      {/* Top University Announcement Bar */}
      <div className="bg-ink px-4 py-2 text-caption text-white/90 dark:bg-dark-surface border-b border-line dark:border-dark-line">
        <div className="mx-auto flex max-w-7xl items-center justify-between text-[12px]">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-risk-low animate-pulse" />
            <span className="font-medium">
              PES Institute of Technology &amp; Management (PESITM) &bull; VTU Affiliated &bull; AICTE Approved
            </span>
          </div>
          <div className="hidden sm:flex items-center gap-4 text-white/70">
            <span>Shivamogga, Karnataka - 577204</span>
            <span>&bull;</span>
            <span className="text-accent font-semibold">Admissions 2026 Open</span>
          </div>
        </div>
      </div>

      {/* Main Sticky Navigation Bar */}
      <header className="sticky top-0 z-50 border-b border-line bg-surface/95 px-6 py-3.5 backdrop-blur-md shadow-subtle dark:border-dark-line dark:bg-dark-surface/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          {/* Logo & College Identity */}
          <Link to="/" className="flex items-center gap-3 text-decoration-none">
            <div className="flex h-10 w-10 items-center justify-center rounded-input bg-accent font-heading text-xl font-bold text-white shadow-subtle">
              P
            </div>
            <div>
              <span className="font-heading text-heading font-bold tracking-tight text-ink dark:text-dark-text">
                PESITM Shivamogga
              </span>
              <p className="text-[11px] font-medium text-muted dark:text-dark-muted">
                Smart College Management System
              </p>
            </div>
          </Link>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-6 text-caption font-semibold text-muted dark:text-dark-muted">
            <a href="#about" className="hover:text-accent transition">About College</a>
            <a href="#academics" className="hover:text-accent transition">Academics</a>
            <a href="#departments" className="hover:text-accent transition">Departments</a>
            <a href="#announcements" className="hover:text-accent transition">Announcements</a>
            <a href="#contact" className="hover:text-accent transition">Contact</a>
          </nav>

          {/* Primary Action Button: Navigates to 5-Portal Login */}
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate('/login')}
              className="gap-2"
            >
              <span>Portal Login</span>
              <ArrowRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-line bg-surface px-6 py-16 sm:py-24 dark:border-dark-line dark:bg-dark-surface">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-pill bg-accent/10 px-3 py-1 text-caption font-semibold text-accent">
                <Sparkles className="h-3.5 w-3.5" />
                <span>Next-Generation Autonomous Campus Platform</span>
              </div>

              <h1 className="mt-4 font-heading text-4xl font-bold tracking-tight text-ink sm:text-5xl lg:text-6xl dark:text-dark-text">
                Centralized Academic Governance &amp; Intelligent Monitoring
              </h1>

              <p className="mt-4 text-body text-muted dark:text-dark-muted leading-relaxed max-w-xl">
                A modern college management system linking <b>Students, Parents, Teachers, Administrators, and Leadership</b>. Real-time attendance compliance, Continuous Internal Evaluation (CIE), and transparent progress reporting.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => navigate('/login')}
                >
                  <span>Select User Portal</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>

                <a
                  href="#academics"
                  className="inline-flex items-center justify-center rounded-input border border-line bg-page px-5 py-2.5 text-heading font-medium text-ink transition hover:bg-line/70 dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                >
                  Explore Academics
                </a>
              </div>

              {/* Accreditations Row */}
              <div className="mt-8 flex items-center gap-4 text-[12px] font-medium text-muted dark:text-dark-muted">
                <span>&bull; VTU Affiliation Code: <b>4PM</b></span>
                <span>&bull; NAAC Accredited</span>
                <span>&bull; AICTE Approved</span>
              </div>
            </div>

            {/* Hero Interactive Portal Cards Preview */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div
                onClick={() => navigate('/login/student')}
                className="rounded-card border border-line bg-page/50 p-4 transition-all hover:border-accent hover:shadow-subtle cursor-pointer dark:border-dark-line dark:bg-dark-page/40"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-emerald-500/10 text-emerald-600">
                  <GraduationCap className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-dark-text">Student Portal</h3>
                <p className="mt-1 text-caption text-muted">Attendance, CIE marks, GPA trajectory &amp; study materials.</p>
              </div>

              <div
                onClick={() => navigate('/login/parent')}
                className="rounded-card border border-line bg-page/50 p-4 transition-all hover:border-accent hover:shadow-subtle cursor-pointer dark:border-dark-line dark:bg-dark-page/40"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-amber-500/10 text-amber-600">
                  <Users className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-dark-text">Parent Portal</h3>
                <p className="mt-1 text-caption text-muted">Child progress monitoring, attendance shortage warnings &amp; remarks.</p>
              </div>

              <div
                onClick={() => navigate('/login/teacher')}
                className="rounded-card border border-line bg-page/50 p-4 transition-all hover:border-accent hover:shadow-subtle cursor-pointer dark:border-dark-line dark:bg-dark-page/40"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-blue-500/10 text-blue-600">
                  <BookOpen className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-dark-text">Teacher Portal</h3>
                <p className="mt-1 text-caption text-muted">Class management, attendance logging, CIE grading &amp; parent alerts.</p>
              </div>

              <div
                onClick={() => navigate('/login/principal')}
                className="rounded-card border border-line bg-page/50 p-4 transition-all hover:border-accent hover:shadow-subtle cursor-pointer dark:border-dark-line dark:bg-dark-page/40"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-rose-500/10 text-rose-600">
                  <Award className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-dark-text">Principal Portal</h3>
                <p className="mt-1 text-caption text-muted">College-wide analytics, department benchmarking &amp; executive audits.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Metrics Bar */}
      <section className="border-b border-line bg-page/80 py-8 px-6 dark:border-dark-line dark:bg-dark-page/80">
        <div className="mx-auto max-w-7xl grid grid-cols-2 gap-4 md:grid-cols-4 text-center">
          <div>
            <p className="font-heading text-3xl font-bold text-accent">4+</p>
            <p className="mt-1 text-caption text-muted font-medium">Core Engineering Branches</p>
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-ink dark:text-dark-text">100%</p>
            <p className="mt-1 text-caption text-muted font-medium">Outcome-Based Education (OBE)</p>
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-risk-low">75%+</p>
            <p className="mt-1 text-caption text-muted font-medium">VTU Regulatory Attendance Monitoring</p>
          </div>
          <div>
            <p className="font-heading text-3xl font-bold text-ink dark:text-dark-text">5 Portals</p>
            <p className="mt-1 text-caption text-muted font-medium">Dedicated Role-Based Access</p>
          </div>
        </div>
      </section>

      {/* About College Section */}
      <section id="about" className="py-16 px-6 border-b border-line bg-surface dark:border-dark-line dark:bg-dark-surface">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <span className="font-heading text-caption font-semibold uppercase tracking-wider text-accent">
              About The Institution
            </span>
            <h2 className="mt-2 font-heading text-3xl font-bold text-ink dark:text-dark-text">
              PES Institute of Technology &amp; Management (PESITM)
            </h2>
            <p className="mt-3 text-body text-muted dark:text-dark-muted leading-relaxed">
              Established under the esteemed Prerana Educational Trust, PESITM Shivamogga stands as a beacon of academic excellence in Malnad region. We nurture innovative engineers equipped with technical prowess, leadership ethics, and research mindset.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <div className="flex h-10 w-10 items-center justify-center rounded-input bg-accent/10 text-accent">
                <School className="h-5 w-5" />
              </div>
              <h3 className="mt-4 font-heading font-semibold text-heading text-ink dark:text-dark-text">Our Vision</h3>
              <p className="mt-2 text-caption text-muted dark:text-dark-muted leading-relaxed">
                To emerge as a premier institution imparting industry-aligned technical education and fostering societal transformation through cutting-edge engineering.
              </p>
            </Card>

            <Card>
              <div className="flex h-10 w-10 items-center justify-center rounded-input bg-accent/10 text-accent">
                <BookOpen className="h-5 w-5" />
              </div>
              <h3 className="mt-4 font-heading font-semibold text-heading text-ink dark:text-dark-text">Our Mission</h3>
              <p className="mt-2 text-caption text-muted dark:text-dark-muted leading-relaxed">
                Deliver outcome-based curriculum, state-of-the-art laboratory infrastructure, and faculty mentorship that empowers graduates to excel in global engineering frontiers.
              </p>
            </Card>

            <Card>
              <div className="flex h-10 w-10 items-center justify-center rounded-input bg-accent/10 text-accent">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="mt-4 font-heading font-semibold text-heading text-ink dark:text-dark-text">Smart Campus</h3>
              <p className="mt-2 text-caption text-muted dark:text-dark-muted leading-relaxed">
                Equipped with fiber-optic campus intranet, automated RFID attendance, cloud-hosted learning resources, and continuous internal assessment analytics.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* Academic Information Section */}
      <section id="academics" className="py-16 px-6 border-b border-line bg-page dark:border-dark-line dark:bg-dark-page">
        <div className="mx-auto max-w-7xl">
          <div className="max-w-2xl">
            <span className="font-heading text-caption font-semibold uppercase tracking-wider text-accent">
              Academic Framework
            </span>
            <h2 className="mt-2 font-heading text-3xl font-bold text-ink dark:text-dark-text">
              Curriculum, Assessment Scheme &amp; Regulations
            </h2>
            <p className="mt-3 text-body text-muted dark:text-dark-muted leading-relaxed">
              Governed by Visvesvaraya Technological University (VTU) Choice Based Credit System (CBCS) and National Education Policy guidelines.
            </p>
          </div>

          <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="rounded-card border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
              <span className="font-heading text-2xl font-bold text-accent">01</span>
              <h4 className="mt-2 font-semibold text-ink dark:text-dark-text">Continuous Internal Evaluation (CIE)</h4>
              <p className="mt-1 text-caption text-muted">
                Three mandatory internal tests, assignments, quizzes, and project evaluations totaling 50 marks per semester course.
              </p>
            </div>

            <div className="rounded-card border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
              <span className="font-heading text-2xl font-bold text-risk-low">02</span>
              <h4 className="mt-2 font-semibold text-ink dark:text-dark-text">75% Attendance Requirement</h4>
              <p className="mt-1 text-caption text-muted">
                Strict compliance threshold. Automatic alerts trigger to students and registered parents when cumulative attendance dips below 75%.
              </p>
            </div>

            <div className="rounded-card border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
              <span className="font-heading text-2xl font-bold text-accent">03</span>
              <h4 className="mt-2 font-semibold text-ink dark:text-dark-text">Choice Based Credit System (CBCS)</h4>
              <p className="mt-1 text-caption text-muted">
                160 cumulative credits across 8 semesters, incorporating core engineering, inter-disciplinary electives, and capstone research.
              </p>
            </div>

            <div className="rounded-card border border-line bg-surface p-5 dark:border-dark-line dark:bg-dark-surface">
              <span className="font-heading text-2xl font-bold text-purple-600">04</span>
              <h4 className="mt-2 font-semibold text-ink dark:text-dark-text">Transparent Mentoring</h4>
              <p className="mt-1 text-caption text-muted">
                Every batch of 20 students is allocated a dedicated faculty mentor providing academic, personal, and career guidance.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Academic Departments & Branches Section */}
      <section id="departments" className="py-16 px-6 border-b border-line bg-surface dark:border-dark-line dark:bg-dark-surface">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div className="max-w-2xl">
              <span className="font-heading text-caption font-semibold uppercase tracking-wider text-accent">
                Academic Programs &amp; Faculty
              </span>
              <h2 className="mt-2 font-heading text-3xl font-bold text-ink dark:text-dark-text">
                Academic Departments &amp; Branches
              </h2>
              <p className="mt-3 text-body text-muted dark:text-dark-muted leading-relaxed">
                PESITM hosts 10 accredited undergraduate engineering streams and 4 foundational basic science &amp; humanities departments, all equipped with advanced laboratories, computing clusters, and industry research centers.
              </p>
            </div>

            {/* Filter Tabs & Search */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
                <input
                  type="text"
                  placeholder="Filter branch..."
                  value={deptSearch}
                  onChange={(e) => setDeptSearch(e.target.value)}
                  className="w-full sm:w-48 pl-9 pr-3 py-1.5 text-caption rounded-input border border-line bg-page text-ink placeholder:text-muted focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-page dark:text-dark-text"
                />
              </div>

              <div className="inline-flex rounded-input border border-line bg-page p-1 dark:border-dark-line dark:bg-dark-page">
                <button
                  type="button"
                  onClick={() => setDeptTab('all')}
                  className={`px-3 py-1 text-[12px] font-medium rounded transition ${
                    deptTab === 'all'
                      ? 'bg-accent text-white shadow-sm'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  All (14)
                </button>
                <button
                  type="button"
                  onClick={() => setDeptTab('engineering')}
                  className={`px-3 py-1 text-[12px] font-medium rounded transition ${
                    deptTab === 'engineering'
                      ? 'bg-accent text-white shadow-sm'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  Engineering (10)
                </button>
                <button
                  type="button"
                  onClick={() => setDeptTab('basic_science')}
                  className={`px-3 py-1 text-[12px] font-medium rounded transition ${
                    deptTab === 'basic_science'
                      ? 'bg-accent text-white shadow-sm'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  Sciences &amp; Humanities (4)
                </button>
              </div>
            </div>
          </div>

          {/* Branches Grid */}
          <div className="mt-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBranches.map((dept) => (
              <Card key={dept.code} className={`border-l-4 ${dept.borderColor} flex flex-col justify-between hover:shadow-md transition`}>
                <div>
                  <div className="flex items-center justify-between gap-2">
                    <span className={`rounded-pill px-2.5 py-0.5 text-[11px] font-bold uppercase tracking-wider ${dept.badgeColor}`}>
                      {dept.code}
                    </span>
                    <span className="text-[11px] font-medium text-muted dark:text-dark-muted">
                      {dept.categoryLabel}
                    </span>
                  </div>

                  <h3 className="mt-3 font-heading text-lg font-bold text-ink dark:text-dark-text leading-snug">
                    {dept.name}
                  </h3>

                  <p className="mt-2 text-caption text-muted dark:text-dark-muted leading-relaxed line-clamp-3">
                    {dept.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-line/60 dark:border-dark-line/60 space-y-1.5 text-[11px]">
                  <div className="flex justify-between items-center text-muted">
                    <span className="font-medium text-ink dark:text-dark-text">HoD:</span>
                    <span>{dept.head}</span>
                  </div>
                  <div className="flex justify-between items-center text-muted">
                    <span className="font-medium text-ink dark:text-dark-text">Intake:</span>
                    <span>{dept.intake}</span>
                  </div>
                  <div className="text-muted line-clamp-1">
                    <span className="font-medium text-ink dark:text-dark-text">Labs: </span>
                    <span>{dept.labs}</span>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {filteredBranches.length === 0 && (
            <div className="mt-8 rounded-card border border-dashed border-line p-8 text-center text-muted dark:border-dark-line">
              No academic departments matched your filter query "{deptSearch}".
            </div>
          )}
        </div>
      </section>

      {/* Announcements & Notice Board Section */}
      <section id="announcements" className="py-16 px-6 border-b border-line bg-page dark:border-dark-line dark:bg-dark-page">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="font-heading text-caption font-semibold uppercase tracking-wider text-accent">
                Campus Updates
              </span>
              <h2 className="mt-2 font-heading text-3xl font-bold text-ink dark:text-dark-text">
                Official Announcements &amp; Circulars
              </h2>
            </div>
            <span className="text-caption text-muted">Updated daily by Academic Registrar</span>
          </div>

          <div className="mt-8 space-y-3">
            <div className="flex items-start gap-4 rounded-card border border-line bg-surface p-4 transition hover:border-accent dark:border-dark-line dark:bg-dark-surface">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-input bg-accent/10 text-accent font-heading font-bold text-caption">
                OCT 31
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="rounded-pill bg-risk-high/10 px-2 py-0.5 text-[10px] font-semibold text-risk-high">
                    Urgent Circular
                  </span>
                  <h4 className="font-semibold text-ink dark:text-dark-text">
                    VTU Odd Semester Continuous Internal Evaluation (CIE-2) Timetable Released
                  </h4>
                </div>
                <p className="mt-1 text-caption text-muted">
                  The schedule for CIE-2 assessment across 3rd, 5th, and 7th semester engineering courses commences from November 10th. Students must maintain minimum 75% attendance to qualify.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 rounded-card border border-line bg-surface p-4 transition hover:border-accent dark:border-dark-line dark:bg-dark-surface">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-input bg-risk-low/10 text-risk-low font-heading font-bold text-caption">
                OCT 28
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="rounded-pill bg-risk-low/10 px-2 py-0.5 text-[10px] font-semibold text-risk-low">
                    Placements
                  </span>
                  <h4 className="font-semibold text-ink dark:text-dark-text">
                    Campus Placement Drive for Final Year B.E. Students (2025-26 Batch)
                  </h4>
                </div>
                <p className="mt-1 text-caption text-muted">
                  Tier-1 technology recruiters scheduled for campus recruitment rounds. Eligible students with CGPA &ge; 7.0 and zero backlogs must register through the Training &amp; Placement cell.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 rounded-card border border-line bg-surface p-4 transition hover:border-accent dark:border-dark-line dark:bg-dark-surface">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-input bg-purple-500/10 text-purple-600 font-heading font-bold text-caption">
                OCT 24
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="rounded-pill bg-purple-100 px-2 py-0.5 text-[10px] font-semibold text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                    Parent Advisory
                  </span>
                  <h4 className="font-semibold text-ink dark:text-dark-text">
                    Parent-Teacher Interaction Meeting for 5th Semester Classes
                  </h4>
                </div>
                <p className="mt-1 text-caption text-muted">
                  Departmental faculty mentors will host one-on-one counseling sessions with registered parents to review semester progress, attendance records, and university exam preparation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact & Location Section */}
      <section id="contact" className="py-16 px-6 bg-surface dark:bg-dark-surface">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div>
              <span className="font-heading text-caption font-semibold uppercase tracking-wider text-accent">
                Connect With Us
              </span>
              <h2 className="mt-2 font-heading text-3xl font-bold text-ink dark:text-dark-text">
                Contact &amp; Campus Location
              </h2>
              <p className="mt-3 text-body text-muted dark:text-dark-muted leading-relaxed">
                Reach out to the administrative registrar, admissions desk, or individual academic departments.
              </p>

              <div className="mt-8 space-y-4">
                <div className="flex items-start gap-3.5 text-caption">
                  <MapPin className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-ink dark:text-dark-text">Campus Address:</span>
                    <p className="text-muted dark:text-dark-muted">
                      PES Institute of Technology and Management, NH 206, Sagar Road, Shivamogga, Karnataka - 577204
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 text-caption">
                  <Phone className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-ink dark:text-dark-text">Telephone &amp; Help Desk:</span>
                    <p className="text-muted dark:text-dark-muted">
                      +91 8182 264000 &bull; +91 8182 264001 (Mon-Sat, 9:00 AM - 5:00 PM)
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 text-caption">
                  <Mail className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                  <div>
                    <span className="font-semibold text-ink dark:text-dark-text">Email Inquiries:</span>
                    <p className="text-muted dark:text-dark-muted">
                      info@pesitm.edu &bull; principal@pesitm.edu &bull; admissions@pesitm.edu
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Inquiry Form */}
            <Card>
              <h3 className="font-heading text-heading font-semibold text-ink dark:text-dark-text">
                Send an Academic Inquiry
              </h3>
              <p className="mt-1 text-caption text-muted">
                Our academic counseling staff will respond within one business day.
              </p>

              <form onSubmit={handleContactSubmit} className="mt-5 space-y-3.5">
                <div>
                  <label className="block text-caption font-medium mb-1 text-ink dark:text-dark-text">Full Name *</label>
                  <input
                    type="text"
                    required
                    value={contactForm.name}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    placeholder="Enter your name"
                    className="w-full rounded-input border border-line bg-surface px-3.5 py-2 text-body text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <label className="block text-caption font-medium mb-1 text-ink dark:text-dark-text">Email Address *</label>
                    <input
                      type="email"
                      required
                      value={contactForm.email}
                      onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                      placeholder="e.g. you@example.com"
                      className="w-full rounded-input border border-line bg-surface px-3.5 py-2 text-body text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                    />
                  </div>

                  <div>
                    <label className="block text-caption font-medium mb-1 text-ink dark:text-dark-text">Phone Number</label>
                    <input
                      type="tel"
                      value={contactForm.phone}
                      onChange={(e) => setContactForm({ ...contactForm, phone: e.target.value })}
                      placeholder="+91 98450 00000"
                      className="w-full rounded-input border border-line bg-surface px-3.5 py-2 text-body text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-caption font-medium mb-1 text-ink dark:text-dark-text">Message *</label>
                  <textarea
                    rows={3}
                    required
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    placeholder="Provide details about your query..."
                    className="w-full rounded-input border border-line bg-surface p-3 text-body text-ink focus:border-accent focus:outline-none dark:border-dark-line dark:bg-dark-surface dark:text-dark-text"
                  />
                </div>

                <Button type="submit" variant="primary" className="w-full">
                  Submit Inquiry
                </Button>
              </form>
            </Card>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-line bg-ink px-6 py-8 text-white/80 dark:border-dark-line">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-4 text-caption">
          <div>
            <span className="font-heading font-bold text-white text-body">
              PES Institute of Technology &amp; Management, Shivamogga
            </span>
            <p className="mt-1 text-white/60 text-[11px]">
              Affiliated to VTU Belagavi &bull; Approved by AICTE &bull; Recognized by Govt. of Karnataka
            </p>
          </div>

          <div className="flex items-center gap-4">
            <Link to="/login" className="text-accent hover:underline font-semibold">
              Portal Login &rarr;
            </Link>
            <span className="text-white/40">&bull;</span>
            <span className="text-white/60">&copy; 2026 PESITM. All rights reserved.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
