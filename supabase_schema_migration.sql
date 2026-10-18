DO $$
DECLARE
    item_table TEXT;
    id_column TEXT;
    sequence_name TEXT;
    highest_id BIGINT;
    has_legacy_rows BOOLEAN;
BEGIN
    ALTER TABLE public.students ADD COLUMN IF NOT EXISTS course_id INT;

    FOR item_table, id_column IN
        SELECT * FROM (VALUES
            ('users', 'user_id'),
            ('students', 'student_id'),
            ('teachers', 'teacher_id'),
            ('courses', 'course_id'),
            ('attendance', 'attendance_id'),
            ('marks', 'mark_id'),
            ('fees', 'fee_id'),
            ('events', 'event_id')
        ) AS ids(table_name, id_column)
    LOOP
        sequence_name := pg_get_serial_sequence(format('public.%I', item_table), id_column);
        IF sequence_name IS NULL THEN
            sequence_name := format('public.%I', item_table || '_' || id_column || '_seq');
            EXECUTE format('CREATE SEQUENCE IF NOT EXISTS %s', sequence_name);
            EXECUTE format(
                'ALTER SEQUENCE %s OWNED BY public.%I.%I',
                sequence_name, item_table, id_column
            );
        END IF;
        EXECUTE format(
            'ALTER TABLE public.%I ALTER COLUMN %I SET DEFAULT nextval(%L::regclass)',
            item_table, id_column, sequence_name
        );
        EXECUTE format(
            'SELECT COALESCE(MAX(%I), 0) FROM public.%I',
            id_column, item_table
        ) INTO highest_id;
        PERFORM setval(sequence_name::regclass, highest_id + 1, false);
    END LOOP;

    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='students' AND column_name='course'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM public.students
            WHERE course IS NOT NULL AND BTRIM(course) <> '' AND user_id IS NULL
        ) THEN
            RAISE EXCEPTION 'Cannot migrate student courses with missing user ownership.';
        END IF;
        INSERT INTO public.courses (user_id, course_name)
        SELECT DISTINCT students.user_id, NULLIF(BTRIM(students.course), '')
        FROM public.students AS students
        WHERE students.course IS NOT NULL AND BTRIM(students.course) <> ''
          AND NOT EXISTS (
              SELECT 1 FROM public.courses
              WHERE courses.user_id=students.user_id
                AND courses.course_name=NULLIF(BTRIM(students.course), '')
          );
        UPDATE public.students
        SET course_id=courses.course_id
        FROM public.courses
        WHERE students.course_id IS NULL
          AND courses.user_id=students.user_id
          AND courses.course_name=NULLIF(BTRIM(students.course), '');
        ALTER TABLE public.students DROP COLUMN course;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conrelid='public.students'::regclass
          AND conname='fk_student_course'
          AND contype='f'
    ) THEN
        ALTER TABLE public.students
            ADD CONSTRAINT fk_student_course FOREIGN KEY (course_id)
            REFERENCES public.courses(course_id) ON DELETE SET NULL;
    END IF;

    IF to_regclass('public.student_users') IS NOT NULL THEN
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM public.student_users)' INTO has_legacy_rows;
        IF has_legacy_rows THEN
            RAISE EXCEPTION 'Legacy student_users contains data; migrate it before cleanup.';
        END IF;
        ALTER TABLE public.students DROP CONSTRAINT IF EXISTS fk_student_user;
        ALTER TABLE public.students DROP COLUMN IF EXISTS student_user_id;
        DROP TABLE public.student_users;
    END IF;

    IF to_regclass('public.teacher_users') IS NOT NULL THEN
        EXECUTE 'SELECT EXISTS (SELECT 1 FROM public.teacher_users)' INTO has_legacy_rows;
        IF has_legacy_rows THEN
            RAISE EXCEPTION 'Legacy teacher_users contains data; migrate it before cleanup.';
        END IF;
        ALTER TABLE public.teachers DROP CONSTRAINT IF EXISTS fk_teacher_user;
        ALTER TABLE public.teachers DROP COLUMN IF EXISTS teacher_user_id;
        DROP TABLE public.teacher_users;
    END IF;

    FOR item_table IN
        SELECT unnest(ARRAY['students', 'teachers', 'courses', 'attendance', 'marks', 'fees', 'events'])
    LOOP
        EXECUTE format(
            'ALTER TABLE public.%I ALTER COLUMN user_id SET NOT NULL',
            item_table
        );
    END LOOP;
END $$;
