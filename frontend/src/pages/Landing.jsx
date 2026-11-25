import React, { useState, useEffect } from 'react';
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
  ChevronLeft,
  Search,
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import api from '@/services/api';
import PesitmLogo from '@/components/common/PesitmLogo';
import DepartmentDetailsModal from '@/components/departments/DepartmentDetailsModal';
import campusEntrance from '@/assets/hero/campus_entrance.jpg';
import campusAerialGround from '@/assets/hero/campus_aerial_ground.jpg';
import campusMainBuilding from '@/assets/hero/campus_main_building.jpg';

const ACADEMIC_BRANCHES = [
  // 1. Electronics & Communications Engineering (Image 2 Card 1)
  {
    code: 'ECE',
    name: 'Electronics & Communications Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-indigo-600',
    badgeColor: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
    head: 'Dr. Vishnu V M',
    designation: 'Associate Professor & Head',
    email: 'hodece@pestrust.edu.in',
    phone: '+91 94482 10003',
    intake: '120 Seats',
    labs: 'VLSI Chip Design Center, Advanced DSP Lab, RF & Microwave Telemetry Lab, IoT Embedded Lab',
    description: 'NBA & NAAC accredited department functioning since inception. Advanced studies in VLSI semiconductor design, embedded microcontrollers, IoT sensor telemetry, wireless communications, and digital signal processing.',
    faculty: [
      { teacher_id: 101, name: 'Dr. Nandan N Shenoy', designation: 'Associate Professor', email: 'nandan.ece@pestrust.edu.in' },
      { teacher_id: 102, name: 'Mrs. Shyamala S C', designation: 'Assistant Professor', email: 'shyamala.ece@pestrust.edu.in' },
      { teacher_id: 7, name: 'Dr. Geetha K', designation: 'Professor', email: 'geetha.k@pesitm.edu' },
      { teacher_id: 8, name: 'Prof. Sneha Hegde', designation: 'Assistant Professor', email: 'sneha.hegde@pesitm.edu' },
      { teacher_id: 9, name: 'Prof. Ramesh Babu', designation: 'Associate Professor', email: 'ramesh.babu@pesitm.edu' }
    ]
  },
  // 2. Electrical & Electronics Engineering (Image 2 Card 2)
  {
    code: 'EEE',
    name: 'Electrical & Electronics Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-yellow-600',
    badgeColor: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    head: 'Dr. Om Prakash Yadav',
    designation: 'Professor & Head',
    email: 'hodeee@pestrust.edu.in',
    phone: '+91 94482 10004',
    intake: '60 Seats',
    labs: 'Power Electronics Lab, Electric Drives Lab, Smart Grid & Renewable Energy Center',
    description: 'Mastering electrical power generation, renewable solar/wind integration, power systems analysis, electric vehicle drives, and embedded industrial automation.',
    faculty: [
      { teacher_id: 103, name: 'Dr. Basavaraj G', designation: 'Associate Professor', email: 'basavaraj.eee@pestrust.edu.in' },
      { teacher_id: 104, name: 'Prof. Suresh K', designation: 'Assistant Professor', email: 'suresh.eee@pestrust.edu.in' },
      { teacher_id: 105, name: 'Prof. Preethi R', designation: 'Assistant Professor', email: 'preethi.eee@pestrust.edu.in' }
    ]
  },
  // 3. Information Science & Engineering (Image 2 Card 3)
  {
    code: 'ISE',
    name: 'Information Science & Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-emerald-600',
    badgeColor: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300',
    head: 'Dr. Mouneshachari S',
    designation: 'Professor & Head',
    email: 'hodise@pestrust.edu.in',
    phone: '+91 94482 10002',
    intake: '120 Seats',
    labs: 'Enterprise Software Studio, Big Data Pipelines Lab, Modern DevOps Cloud Hub',
    description: 'Focused on enterprise software systems, data engineering pipelines, distributed networks, cloud security protocols, and modern DevOps agile delivery practices.',
    faculty: [
      { teacher_id: 106, name: 'Mr. Vinay S K', designation: 'Assistant Professor', email: 'vinay.ise@pestrust.edu.in' },
      { teacher_id: 107, name: 'Mr. Madesha M', designation: 'Assistant Professor', email: 'madesha.ise@pestrust.edu.in' },
      { teacher_id: 108, name: 'Mr. Rudresh N C', designation: 'Assistant Professor', email: 'rudresh.ise@pestrust.edu.in' },
      { teacher_id: 5, name: 'Prof. Deepa Patil', designation: 'Assistant Professor', email: 'deepa.patil@pesitm.edu' },
      { teacher_id: 6, name: 'Prof. Harish Gowda', designation: 'Associate Professor', email: 'harish.gowda@pesitm.edu' }
    ]
  },
  // 4. Computer Science & Engineering (Image 2 Card 4)
  {
    code: 'CSE',
    name: 'Computer Science & Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-blue-600',
    badgeColor: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    head: 'Dr. Prasanna Kumar H R',
    designation: 'Professor & Head',
    email: 'hodcse@pestrust.edu.in',
    phone: '+91 94482 10001',
    intake: '180 Seats',
    labs: 'High-Performance GPU Cluster, Cloud Systems Lab, Cyber Security Center, Open Source Hub',
    description: 'NBA accredited flagship program with specializations in Machine Learning, Cloud Systems, Big Data, and Cyber Security. High-speed GPU computing infrastructure for student project development.',
    faculty: [
      { teacher_id: 109, name: 'Dr. Manu A P', designation: 'Professor', email: 'manu.cse@pestrust.edu.in' },
      { teacher_id: 110, name: 'Dr. Chethan L S', designation: 'Professor', email: 'chethan.cse@pestrust.edu.in' },
      { teacher_id: 1, name: 'Prof. Anita Rao', designation: 'Associate Professor', email: 'anita.rao@pesitm.edu' },
      { teacher_id: 2, name: 'Prof. Karthik Nair', designation: 'Assistant Professor', email: 'karthik.nair@pesitm.edu' },
      { teacher_id: 3, name: 'Dr. Sunil Kumar', designation: 'Professor', email: 'sunil.kumar@pesitm.edu' }
    ]
  },
  // 5. Mechanical Engineering (Image 2 Card 5)
  {
    code: 'ME',
    name: 'Mechanical Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-red-600',
    badgeColor: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    head: 'Dr. Girisha L',
    designation: 'Professor & Head',
    email: 'hodme@pestrust.edu.in',
    phone: '+91 94482 10005',
    intake: '60 Seats',
    labs: 'Robotics & Mechatronics Lab, CNC Precision Machining Lab, Thermal Engineering Center',
    description: 'Encompassing CAD/CAM computer-aided engineering, robotics, thermal dynamics, additive 3D manufacturing, fluid mechanics, and sustainable automotive systems.',
    faculty: [
      { teacher_id: 111, name: 'Dr. Chandrashekar B', designation: 'Professor', email: 'chandrashekar.me@pestrust.edu.in' },
      { teacher_id: 112, name: 'Prof. Naveen Kumar', designation: 'Assistant Professor', email: 'naveen.me@pestrust.edu.in' },
      { teacher_id: 113, name: 'Prof. Manjunatha P', designation: 'Assistant Professor', email: 'manjunatha.me@pestrust.edu.in' }
    ]
  },
  // 6. Civil Engineering (Image 2 Card 6)
  {
    code: 'CV',
    name: 'Civil Engineering',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1541888946425-d0fbb18086f6?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-amber-600',
    badgeColor: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
    head: 'Dr. Harish Kumar S',
    designation: 'Associate Professor & Head',
    email: 'hodcv@pestrust.edu.in',
    phone: '+91 94482 10006',
    intake: '60 Seats',
    labs: 'Structural Dynamics Lab, Geotechnical Eng Lab, CAD Center, Environmental Eng Lab',
    description: 'Focusing on structural mechanics, transportation networks, environmental hydraulics, green architecture, surveying, and smart urban infrastructure planning.',
    faculty: [
      { teacher_id: 114, name: 'Dr. Arjun U', designation: 'Associate Professor', email: 'arjun.cv@pestrust.edu.in' },
      { teacher_id: 115, name: 'Prof. Rajesh V', designation: 'Assistant Professor', email: 'rajesh.cv@pestrust.edu.in' },
      { teacher_id: 116, name: 'Prof. Kavitha N', designation: 'Assistant Professor', email: 'kavitha.cv@pestrust.edu.in' }
    ]
  },
  // 7. Artificial Intelligence & Machine Learning
  {
    code: 'AIML',
    name: 'Artificial Intelligence & Machine Learning',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1677442136019-21780efad99a?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-violet-600',
    badgeColor: 'bg-violet-100 text-violet-800 dark:bg-violet-900/30 dark:text-violet-300',
    head: 'Dr. Likewin Thomas',
    designation: 'Professor & Head',
    email: 'hodaiml@pestrust.edu.in',
    phone: '+91 94482 10007',
    intake: '60 Seats',
    labs: 'Deep Learning Vision Lab, Generative AI Studio, Autonomous Agents Sandbox',
    description: 'Dedicated to neural networks, computer vision, natural language processing, LLMs, reinforcement learning, and ethical predictive AI system deployment.',
    faculty: [
      { teacher_id: 117, name: 'Dr. Shilpa K', designation: 'Associate Professor', email: 'shilpa.aiml@pestrust.edu.in' },
      { teacher_id: 118, name: 'Prof. Kiran M', designation: 'Assistant Professor', email: 'kiran.aiml@pestrust.edu.in' },
      { teacher_id: 119, name: 'Prof. Soumya R', designation: 'Assistant Professor', email: 'soumya.aiml@pestrust.edu.in' }
    ]
  },
  // 8. Computer Science & Design
  {
    code: 'CSD',
    name: 'Computer Science & Design',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1561070791-2526d30994b5?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-purple-600',
    badgeColor: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
    head: 'Dr. Pramod',
    designation: 'Professor & Head',
    email: 'hodcsd@pestrust.edu.in',
    phone: '+91 94482 10008',
    intake: '60 Seats',
    labs: 'HCI Usability Lab, AR/VR Interactive Simulation Lab, Digital Media Production Studio',
    description: 'Blending computational software engineering with human-computer interaction (HCI), UI/UX product design, interactive 3D graphics, and digital media technology.',
    faculty: [
      { teacher_id: 10, name: 'Dr. Vinayaka B', designation: 'Associate Professor', email: 'vinayaka.b@pesitm.edu' },
      { teacher_id: 11, name: 'Prof. Divya Shenoy', designation: 'Assistant Professor', email: 'divya.shenoy@pesitm.edu' },
      { teacher_id: 12, name: 'Prof. Raghavendra S', designation: 'Assistant Professor', email: 'raghavendra.s@pesitm.edu' }
    ]
  },
  // 9. Computer Science & Engineering (Data Science)
  {
    code: 'DS',
    name: 'Computer Science & Engineering (Data Science)',
    category: 'engineering',
    categoryLabel: 'Engineering Discipline (B.E.)',
    imageUrl: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-teal-600',
    badgeColor: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
    head: 'Dr. Sunitha B S',
    designation: 'Professor & Head',
    email: 'hodds@pestrust.edu.in',
    phone: '+91 94482 10009',
    intake: '60 Seats',
    labs: 'Big Data Hadoop/Spark Cluster, Business Intelligence Lab, Statistical Modeling Hub',
    description: 'Specializing in massive dataset processing, predictive analytics, statistical hypothesis testing, data visualization, ETL workflows, and quantitative modeling.',
    faculty: [
      { teacher_id: 120, name: 'Dr. Ananth Kumar', designation: 'Associate Professor', email: 'ananth.ds@pestrust.edu.in' },
      { teacher_id: 121, name: 'Prof. Swathi P', designation: 'Assistant Professor', email: 'swathi.ds@pestrust.edu.in' },
      { teacher_id: 122, name: 'Prof. Prashanth H', designation: 'Assistant Professor', email: 'prashanth.ds@pestrust.edu.in' }
    ]
  },
  // 10. Master of Business Administration
  {
    code: 'MBA',
    name: 'Master of Business Administration (MBA)',
    category: 'postgraduate',
    categoryLabel: 'Postgraduate Management (MBA)',
    imageUrl: 'https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-rose-600',
    badgeColor: 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300',
    head: 'Dr. Vikrama D K',
    designation: 'Professor & Head',
    email: 'hodmba@pestrust.edu.in',
    phone: '+91 94482 10010',
    intake: '120 Seats',
    labs: 'Business Analytics Lab, Financial Markets Simulation Lab, Executive Case Room',
    description: 'Advanced management education specializing in financial strategies, human capital management, digital marketing analytics, and corporate leadership.',
    faculty: [
      { teacher_id: 123, name: 'Dr. D M Arvind Mallik', designation: 'Professor', email: 'arvind.mba@pestrust.edu.in' },
      { teacher_id: 124, name: 'Dr. Jayanthi R', designation: 'Professor', email: 'jayanthi.mba@pestrust.edu.in' },
      { teacher_id: 125, name: 'Prof. Anand V', designation: 'Assistant Professor', email: 'anand.mba@pestrust.edu.in' }
    ]
  },
  // 11. Master of Computer Applications
  {
    code: 'MCA',
    name: 'Master of Computer Applications (MCA)',
    category: 'postgraduate',
    categoryLabel: 'Postgraduate Computing (MCA)',
    imageUrl: 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-blue-700',
    badgeColor: 'bg-blue-100 text-blue-900 dark:bg-blue-900/40 dark:text-blue-200',
    head: 'Dr. Sanjay K S',
    designation: 'Professor & Head',
    email: 'hodmca@pestrust.edu.in',
    phone: '+91 94482 10011',
    intake: '60 Seats',
    labs: 'Cloud Computing Architecture Center, Full-Stack Web Development Lab, Enterprise Systems',
    description: 'Postgraduate curriculum emphasizing enterprise software design, full-stack frameworks, cloud-native deployments, and advanced database engineering.',
    faculty: [
      { teacher_id: 126, name: 'Dr. Gururaj H', designation: 'Associate Professor', email: 'gururaj.mca@pestrust.edu.in' },
      { teacher_id: 127, name: 'Prof. Rekha B', designation: 'Assistant Professor', email: 'rekha.mca@pestrust.edu.in' },
      { teacher_id: 128, name: 'Prof. Santosh K', designation: 'Assistant Professor', email: 'santosh.mca@pestrust.edu.in' }
    ]
  },
  // 12. Department of Physics
  {
    code: 'PHY',
    name: 'Department of Physics',
    category: 'basic_science',
    categoryLabel: 'Basic Sciences & Humanities',
    imageUrl: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-sky-600',
    badgeColor: 'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300',
    head: 'Dr. Pramod Gopal Pai',
    designation: 'Associate Professor & Head',
    email: 'hodphy@pestrust.edu.in',
    phone: '+91 94482 10012',
    intake: 'All 1st Year Streams',
    labs: 'Engineering Physics Lab, Optics & Laser Research Lab, Nanotechnology Studio',
    description: 'Foundational and applied physics covering semiconductor physics, lasers, quantum mechanics, electromagnetism, and advanced nanotechnology materials.',
    faculty: [
      { teacher_id: 129, name: 'Dr. Jagadeesh M', designation: 'Assistant Professor', email: 'jagadeesh.phy@pestrust.edu.in' },
      { teacher_id: 130, name: 'Prof. Rashmi S', designation: 'Assistant Professor', email: 'rashmi.phy@pestrust.edu.in' }
    ]
  },
  // 13. Department of Chemistry
  {
    code: 'CHEM',
    name: 'Department of Chemistry',
    category: 'basic_science',
    categoryLabel: 'Basic Sciences & Humanities',
    imageUrl: 'https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-lime-600',
    badgeColor: 'bg-lime-100 text-lime-800 dark:bg-lime-900/30 dark:text-lime-300',
    head: 'Dr. Mohan Kumar',
    designation: 'Associate Professor & Head',
    email: 'hodchem@pestrust.edu.in',
    phone: '+91 94482 10013',
    intake: 'All 1st Year Streams',
    labs: 'Engineering Chemistry Lab, Instrumental Analysis Center, Corrosion & Battery Research Lab',
    description: 'Engineering chemistry focusing on polymer materials, electrochemical energy storage, water purification, smart coatings, and battery cell nanotechnology.',
    faculty: [
      { teacher_id: 131, name: 'Dr. Vinutha K', designation: 'Assistant Professor', email: 'vinutha.chem@pestrust.edu.in' },
      { teacher_id: 132, name: 'Prof. Prakash N', designation: 'Assistant Professor', email: 'prakash.chem@pestrust.edu.in' }
    ]
  },
  // 14. Department of Mathematics
  {
    code: 'MATH',
    name: 'Department of Mathematics',
    category: 'basic_science',
    categoryLabel: 'Basic Sciences & Humanities',
    imageUrl: 'https://images.unsplash.com/photo-1635070041409-e63e783ee3c1?auto=format&fit=crop&w=800&q=80',
    borderColor: 'border-l-pink-600',
    badgeColor: 'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',
    head: 'Dr. Basavaraj M',
    designation: 'Professor & Head',
    email: 'hodmat@pestrust.edu.in',
    phone: '+91 94482 10014',
    intake: 'All 1st & 2nd Year Streams',
    labs: 'Computational Mathematics Lab, Numerical Analysis Center, MATLAB & SageMath Studio',
    description: 'Providing rigorous mathematical foundations in multivariable calculus, linear algebra, discrete mathematics, complex variables, and stochastic probability modeling.',
    faculty: [
      { teacher_id: 133, name: 'Dr. Aveesh S T', designation: 'Associate Professor', email: 'aveesh.math@pestrust.edu.in' },
      { teacher_id: 134, name: 'Dr. Mamatha C', designation: 'Assistant Professor', email: 'mamatha.math@pestrust.edu.in' }
    ]
  },
];

const HERO_SLIDES = [
  {
    image: campusEntrance,
    title: 'PESITM Main Entrance & Landmark Portal',
    caption: 'Autonomous Engineering Institution under VTU, Shivamogga'
  },
  {
    image: campusAerialGround,
    title: '50+ Acre Lush Campus & Central Sports Grounds',
    caption: 'Vibrant academic ecosystem and student facilities'
  },
  {
    image: campusMainBuilding,
    title: 'Academic & Administrative Quadrangle Avenue',
    caption: 'Modern research labs, high-tech lecture halls & innovation centers'
  }
];

export default function Landing() {
  const navigate = useNavigate();

  // Hero Campus Background Slideshow State
  const [currentHeroSlide, setCurrentHeroSlide] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentHeroSlide((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 4500);
    return () => clearInterval(timer);
  }, []);

  // Branch filter & search state
  const [branches, setBranches] = useState(ACADEMIC_BRANCHES);
  const [deptTab, setDeptTab] = useState('all'); // 'all' | 'engineering' | 'postgraduate' | 'basic_science'
  const [deptSearch, setDeptSearch] = useState('');

  // Department Details Modal State
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const [isDeptModalOpen, setIsDeptModalOpen] = useState(false);

  const handleOpenDepartment = (dept) => {
    setSelectedDepartment(dept);
    setIsDeptModalOpen(true);
  };

  // Fetch live departments from backend to guarantee real-time sync with database
  useEffect(() => {
    api.get('/public/departments')
      .then((res) => {
        if (res.data?.success && Array.isArray(res.data.data) && res.data.data.length > 0) {
          const apiDepts = res.data.data;
          setBranches((prev) =>
            prev.map((branch) => {
              const matched = apiDepts.find(
                (d) =>
                  d.dept_code?.toUpperCase() === branch.code?.toUpperCase() ||
                  branch.name.toLowerCase().includes(d.name?.toLowerCase()) ||
                  d.name?.toLowerCase().includes(branch.name.toLowerCase())
              );
              if (matched) {
                return {
                  ...branch,
                  head: matched.hod_name || branch.head,
                  designation: matched.hod_designation || branch.designation,
                  email: matched.hod_email || branch.email,
                  phone: matched.hod_phone || branch.phone,
                  faculty: (matched.faculty && matched.faculty.length > 0) ? matched.faculty : branch.faculty,
                };
              }
              return branch;
            })
          );
        }
      })
      .catch(() => {
        // Fallback safely to static ACADEMIC_BRANCHES
      });
  }, []);

  const filteredBranches = branches.filter((b) => {
    const matchesTab =
      deptTab === 'all' ||
      (deptTab === 'engineering' && b.category === 'engineering') ||
      (deptTab === 'postgraduate' && b.category === 'postgraduate') ||
      (deptTab === 'basic_science' && b.category === 'basic_science');
    const matchesSearch =
      deptSearch.trim() === '' ||
      b.name.toLowerCase().includes(deptSearch.toLowerCase()) ||
      b.code.toLowerCase().includes(deptSearch.toLowerCase()) ||
      b.head.toLowerCase().includes(deptSearch.toLowerCase()) ||
      (b.email && b.email.toLowerCase().includes(deptSearch.toLowerCase()));
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
      {/* 1. Official PESITM Top Brand Header (Matching pestrust.edu.in/pesitm Header UI) */}
      <div className="bg-white text-slate-900 border-b border-slate-200 py-3.5 px-4 sm:px-6 dark:bg-slate-950 dark:text-white dark:border-slate-800">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-center gap-3 sm:gap-4 text-center">
          <Link to="/" className="flex flex-col sm:flex-row items-center gap-3 sm:gap-4 text-decoration-none group">
            <PesitmLogo className="h-14 w-14 sm:h-16 sm:w-16 transition-transform group-hover:scale-105" />
            <div className="flex flex-col items-center sm:items-start text-center sm:text-left">
              <h1 className="font-heading text-xl sm:text-2xl md:text-[1.75rem] font-black tracking-tight text-[#0f224a] dark:text-white leading-tight">
                PES Institute of Technology &amp; Management
              </h1>
              
              {/* Red Divider: Autonomous Institute under VTU */}
              <div className="flex items-center justify-center sm:justify-start gap-2 w-full my-0.5">
                <span className="hidden sm:inline-block h-[1.5px] w-8 sm:w-14 bg-red-600"></span>
                <span className="text-xs sm:text-sm font-extrabold text-red-600 uppercase tracking-wider">
                  Autonomous Institute under VTU
                </span>
                <span className="hidden sm:inline-block h-[1.5px] w-8 sm:w-14 bg-red-600"></span>
              </div>

              <p className="text-[11px] sm:text-xs font-medium text-slate-600 dark:text-slate-400">
                NH-206, Sagar Road, Shivamogga - 577204
              </p>
            </div>
          </Link>
        </div>
      </div>

      {/* 2. Official PESITM Dark Navy Navigation Bar (Matching pestrust.edu.in/pesitm) */}
      <header className="sticky top-0 z-40 bg-[#17183B] text-white shadow-md border-b border-indigo-950/60 px-4 sm:px-6">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
          {/* Main Navigation Links */}
          <nav className="hidden lg:flex items-center text-xs font-bold tracking-wide uppercase">
            <a
              href="#"
              className="py-3.5 px-3.5 text-red-500 border-b-2 border-red-500 hover:text-red-400 transition"
            >
              HOME
            </a>
            <a
              href="#about"
              className="py-3.5 px-3.5 text-white/90 hover:text-red-400 transition"
            >
              ABOUT US
            </a>
            <a
              href="#courses-offered"
              className="py-3.5 px-3.5 text-white/90 hover:text-red-400 transition"
            >
              PROGRAMS
            </a>
            <a
              href="#academics"
              className="py-3.5 px-3.5 text-white/90 hover:text-red-400 transition"
            >
              Curriculum, Assessment Scheme & Regulations
            </a>
            <a
              href="#contact"
              className="py-3.5 px-3.5 text-white/90 hover:text-red-400 transition"
            >
              Contact Us
            </a>
            <a
              href="#announcements"
              className="py-3.5 px-3.5 text-white/90 hover:text-red-400 transition"
            >
              Announcements
            </a>
          </nav>

          {/* Mobile brand text */}
          <div className="lg:hidden py-3 text-xs font-bold text-white/90 uppercase tracking-wider flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
            <span>PESITM Navigation</span>
          </div>

          {/* Right Action: Dedicated Portal Login Button */}
          <div className="flex items-center gap-3 py-2">
            <Button
              variant="primary"
              size="sm"
              onClick={() => navigate('/login')}
              className="gap-2 bg-red-600 hover:bg-red-700 text-white font-bold text-xs uppercase tracking-wider shadow-sm border border-red-500"
            >
              <span>Portal Login</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section with Transparent Slideshow of PESITM Campus */}
      <section className="relative overflow-hidden border-b border-line px-6 py-12 sm:py-16 lg:py-20 bg-slate-100 dark:bg-slate-900">
        {/* Dynamic Campus Background Slideshow with Real Images */}
        <div className="absolute inset-0 pointer-events-none z-0 overflow-hidden">
          {HERO_SLIDES.map((slide, idx) => (
            <img
              key={idx}
              src={slide.image}
              alt={slide.title}
              className={`absolute inset-0 w-full h-full object-cover transition-all duration-1000 ease-in-out ${
                idx === currentHeroSlide
                  ? 'opacity-100 scale-100'
                  : 'opacity-0 scale-105'
              }`}
            />
          ))}

          {/* Transparent Soft Tint - so the campus images clearly shine through in the background! */}
          <div className="absolute inset-0 bg-white/40 dark:bg-slate-950/60 backdrop-blur-[0.5px] transition-colors" />
          <div className="absolute inset-0 bg-gradient-to-r from-white/70 via-white/35 to-white/60 dark:from-slate-950/80 dark:via-slate-950/45 dark:to-slate-950/70" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/50 via-transparent to-white/60 dark:from-slate-950/60 dark:via-transparent dark:to-slate-950/70" />
        </div>

        <div className="relative z-10 mx-auto max-w-7xl">
          {/* Hero Header: Full-Width Title (Single Line with Best Modern Typography) */}
          <div className="mb-8 lg:mb-10">
            <div className="inline-flex items-center gap-2 rounded-full bg-accent/10 px-3.5 py-1 text-caption font-semibold text-accent dark:bg-dark-accent/15 dark:text-dark-accent mb-3 shadow-sm backdrop-blur-sm border border-accent/20">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Next-Generation Autonomous Campus Platform &bull; VTU Affiliated (Code: 4PM)</span>
            </div>

            <h1 className="font-heading font-black tracking-[-0.03em] text-ink dark:text-white whitespace-nowrap overflow-visible text-[clamp(1.15rem,2.75vw,2.95rem)] leading-none py-1 drop-shadow-sm">
              <span>Centralized Academic Monitoring and </span>
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 bg-clip-text text-transparent dark:from-blue-400 dark:via-indigo-400 dark:to-violet-400">
                Prediction System
              </span>
            </h1>
          </div>

          <div className="grid grid-cols-1 gap-10 lg:grid-cols-12 lg:items-center">
            <div className="lg:col-span-5">
              <p className="text-body text-slate-700 dark:text-slate-200 leading-relaxed max-w-xl font-medium drop-shadow-sm">
                A modern college management system linking <b>Students, Parents, Teachers, Administrators, and Leadership</b>. Real-time attendance compliance, Continuous Internal Evaluation (CIE), and transparent progress reporting.
              </p>

              <div className="mt-8 flex flex-wrap items-center gap-3">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={() => navigate('/login')}
                  className="shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all"
                >
                  <span>Select User Portal</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>

                <a
                  href="#academics"
                  className="inline-flex items-center justify-center rounded-input border border-slate-300 bg-white/90 px-5 py-2.5 text-heading font-semibold text-ink transition hover:bg-white shadow-sm hover:shadow dark:border-slate-700 dark:bg-slate-800/90 dark:text-dark-text"
                >
                  Explore Academics
                </a>
              </div>

              {/* Accreditations Row */}
              <div className="mt-8 flex flex-wrap items-center gap-4 text-[12px] font-semibold text-slate-700 dark:text-slate-300">
                <span>&bull; VTU Affiliation Code: <b className="text-red-600 dark:text-red-400">4PM</b></span>
                <span>&bull; NAAC Accredited</span>
                <span>&bull; AICTE Approved</span>
              </div>

              {/* Interactive Slideshow Controls */}
              <div className="mt-6 flex items-center gap-2.5 pt-3 border-t border-slate-300/60 dark:border-slate-800/80">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-700 dark:text-slate-300 flex items-center gap-1.5">
                  <span className="relative flex h-2.5 w-2.5">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-red-600"></span>
                  </span>
                  Campus Gallery:
                </span>
                <div className="flex items-center gap-1.5">
                  {HERO_SLIDES.map((slide, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => setCurrentHeroSlide(idx)}
                      className={`h-2.5 rounded-full transition-all duration-300 ${
                        idx === currentHeroSlide
                          ? 'w-7 bg-red-600 shadow-sm'
                          : 'w-2.5 bg-slate-400/60 hover:bg-slate-700 dark:bg-slate-600 dark:hover:bg-slate-400'
                      }`}
                      title={slide.title}
                      aria-label={`Switch to ${slide.title}`}
                    />
                  ))}
                </div>
                <div className="flex items-center gap-1 ml-auto">
                  <button
                    type="button"
                    onClick={() => setCurrentHeroSlide((prev) => (prev - 1 + HERO_SLIDES.length) % HERO_SLIDES.length)}
                    className="p-1 rounded-full bg-white/80 dark:bg-slate-800/80 hover:bg-white dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300/60 dark:border-slate-700 shadow-xs transition"
                    title="Previous campus photo"
                    aria-label="Previous slide"
                  >
                    <ChevronLeft className="h-3.5 w-3.5" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setCurrentHeroSlide((prev) => (prev + 1) % HERO_SLIDES.length)}
                    className="p-1 rounded-full bg-white/80 dark:bg-slate-800/80 hover:bg-white dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-300/60 dark:border-slate-700 shadow-xs transition"
                    title="Next campus photo"
                    aria-label="Next slide"
                  >
                    <ChevronRight className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Hero Interactive Frosted Glass Portal Cards */}
            <div className="lg:col-span-7 grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              <div
                onClick={() => navigate('/login/student')}
                className="group rounded-card border border-white/80 bg-white/85 dark:bg-slate-900/80 dark:border-slate-800/80 backdrop-blur-md p-4 transition-all hover:border-emerald-500 hover:shadow-xl cursor-pointer hover:-translate-y-1 shadow-md"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-emerald-500/10 text-emerald-600 group-hover:scale-110 group-hover:bg-emerald-500/20 transition-all">
                  <GraduationCap className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-white group-hover:text-emerald-600 dark:group-hover:text-emerald-400 transition-colors">Student Portal</h3>
                <p className="mt-1 text-caption text-slate-600 dark:text-slate-300">Attendance, CIE marks, GPA trajectory &amp; study materials.</p>
              </div>

              <div
                onClick={() => navigate('/login/parent')}
                className="group rounded-card border border-white/80 bg-white/85 dark:bg-slate-900/80 dark:border-slate-800/80 backdrop-blur-md p-4 transition-all hover:border-amber-500 hover:shadow-xl cursor-pointer hover:-translate-y-1 shadow-md"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-amber-500/10 text-amber-600 group-hover:scale-110 group-hover:bg-amber-500/20 transition-all">
                  <Users className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors">Parent Portal</h3>
                <p className="mt-1 text-caption text-slate-600 dark:text-slate-300">Child progress monitoring, attendance shortage warnings &amp; remarks.</p>
              </div>

              <div
                onClick={() => navigate('/login/teacher')}
                className="group rounded-card border border-white/80 bg-white/85 dark:bg-slate-900/80 dark:border-slate-800/80 backdrop-blur-md p-4 transition-all hover:border-blue-500 hover:shadow-xl cursor-pointer hover:-translate-y-1 shadow-md"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-blue-500/10 text-blue-600 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all">
                  <BookOpen className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">Teacher Portal</h3>
                <p className="mt-1 text-caption text-slate-600 dark:text-slate-300">Class management, attendance logging, CIE grading &amp; parent alerts.</p>
              </div>

              <div
                onClick={() => navigate('/login/principal')}
                className="group rounded-card border border-white/80 bg-white/85 dark:bg-slate-900/80 dark:border-slate-800/80 backdrop-blur-md p-4 transition-all hover:border-rose-500 hover:shadow-xl cursor-pointer hover:-translate-y-1 shadow-md"
              >
                <div className="flex h-10 w-10 items-center justify-center rounded-input bg-rose-500/10 text-rose-600 group-hover:scale-110 group-hover:bg-rose-500/20 transition-all">
                  <Award className="h-5 w-5" />
                </div>
                <h3 className="mt-3 font-heading font-bold text-ink dark:text-white group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">Principal Portal</h3>
                <p className="mt-1 text-caption text-slate-600 dark:text-slate-300">College-wide analytics, department benchmarking &amp; executive audits.</p>
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

      {/* Courses Offered Section (Matching Image 2 & pestrust.edu.in/pesitm) */}
      <section id="courses-offered" className="py-16 px-6 border-b border-line bg-surface dark:border-dark-line dark:bg-dark-surface">
        <div className="mx-auto max-w-7xl">
          {/* Section Heading with Line (Matching Image 2) */}
          <div className="flex items-center gap-4 mb-6">
            <h2 className="font-heading text-2xl sm:text-3xl font-bold text-ink dark:text-dark-text whitespace-nowrap">
              Courses Offered
            </h2>
            <div className="h-[1.5px] flex-grow bg-slate-300 dark:bg-slate-700"></div>
          </div>

          {/* Subheading & Category Controls */}
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 mb-8">
            <p className="text-body text-muted dark:text-dark-muted max-w-xl">
              PESITM offers accredited Undergraduate, Postgraduate, and Foundational Science programs under Visvesvaraya Technological University (VTU). Click any department to view faculty profiles, research facilities, and curriculum.
            </p>

            {/* Filter Tabs & Search */}
            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
                <input
                  type="text"
                  placeholder="Search department..."
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
                      ? 'bg-red-600 text-white shadow-sm font-bold'
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
                      ? 'bg-red-600 text-white shadow-sm font-bold'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  Engineering (9)
                </button>
                <button
                  type="button"
                  onClick={() => setDeptTab('postgraduate')}
                  className={`px-3 py-1 text-[12px] font-medium rounded transition ${
                    deptTab === 'postgraduate'
                      ? 'bg-red-600 text-white shadow-sm font-bold'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  Postgraduate (2)
                </button>
                <button
                  type="button"
                  onClick={() => setDeptTab('basic_science')}
                  className={`px-3 py-1 text-[12px] font-medium rounded transition ${
                    deptTab === 'basic_science'
                      ? 'bg-red-600 text-white shadow-sm font-bold'
                      : 'text-muted hover:text-ink dark:hover:text-dark-text'
                  }`}
                >
                  Sciences (3)
                </button>
              </div>
            </div>
          </div>

          {/* Department Cards Grid (Matching Image 2 Layout) */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            {filteredBranches.map((dept) => (
              <div
                key={dept.code}
                onClick={() => handleOpenDepartment(dept)}
                className="group relative rounded-xl overflow-hidden border border-slate-200 bg-white shadow-md hover:shadow-2xl transition-all duration-300 cursor-pointer flex flex-col justify-between hover:-translate-y-1.5 dark:border-dark-line dark:bg-dark-surface"
              >
                {/* Photo Banner matching Image 2 */}
                <div className="relative h-52 w-full overflow-hidden bg-slate-100 dark:bg-slate-800">
                  <img
                    src={dept.imageUrl}
                    alt={dept.name}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                    loading="lazy"
                    onError={(e) => {
                      e.target.src = 'https://images.unsplash.com/photo-1562774053-701939374585?auto=format&fit=crop&w=800&q=80';
                    }}
                  />
                  <div className="absolute top-3 left-3 flex items-center gap-1.5">
                    <span className="rounded bg-slate-900/85 backdrop-blur-md px-2 py-0.5 text-[10px] font-bold text-white uppercase tracking-wider">
                      {dept.code}
                    </span>
                    <span className="rounded bg-red-600/90 backdrop-blur-md px-2 py-0.5 text-[10px] font-semibold text-white">
                      {dept.category === 'engineering' ? 'B.E. UG' : dept.category === 'postgraduate' ? 'PG' : 'Sciences'}
                    </span>
                  </div>
                </div>

                {/* Card Title & Content */}
                <div className="p-5 flex flex-col flex-grow justify-between text-center">
                  <div>
                    <h3 className="font-heading text-base sm:text-lg font-bold text-slate-800 dark:text-slate-100 group-hover:text-red-600 dark:group-hover:text-red-400 transition leading-snug">
                      {dept.name}
                    </h3>
                    <p className="mt-1.5 text-xs text-muted dark:text-dark-muted font-medium">
                      HoD: <strong className="text-slate-700 dark:text-slate-300">{dept.head}</strong>
                    </p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-100 dark:border-dark-line flex items-center justify-between text-xs font-semibold text-red-600 dark:text-red-400 group-hover:underline">
                    <span>View Faculty &amp; Details</span>
                    <ArrowRight className="h-3.5 w-3.5 transition-transform group-hover:translate-x-1" />
                  </div>
                </div>
              </div>
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
                      info@pestrust.edu.in &bull; principal@pestrust.edu.in &bull; admissions@pestrust.edu.in
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

      {/* Interactive Department Details & Faculty Modal */}
      <DepartmentDetailsModal
        isOpen={isDeptModalOpen}
        onClose={() => setIsDeptModalOpen(false)}
        department={selectedDepartment}
      />
    </div>
  );
}
