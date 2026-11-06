import { Button, Form } from "semantic-ui-react";
import { useFormik } from "formik";
import * as Yup from "yup";
import { toast } from "react-toastify";
import { Link, useNavigate } from "react-router-dom";
import { registerApi } from "../../api/user";

export function Register() {
  const navigate = useNavigate();

  const formik = useFormik({
    initialValues: initialValues(),
    validationSchema: validationSchema(),
    onSubmit: async ({ username, email, password }) => {
      try {
        await registerApi({ username, email, password });
        toast.success("Usuario registrado. Ya puedes iniciar sesión.");
        navigate("/login");
      } catch (error) {
        toast.error(error.message);
      }
    },
  });

  return (
    <div className="register-admin">
      <div className="register-admin__content">
        <h1>Registro</h1>

        <Form className="register-form-admin" onSubmit={formik.handleSubmit}>
          <label>Usuario</label>
          <Form.Input
            name="username"
            placeholder="Usuario"
            autoComplete="username"
            value={formik.values.username}
            onChange={(e) => {
              // Elimina los espacios en tiempo real.
              const value = e.target.value.replace(/\s+/g, "");
              formik.setFieldValue("username", value);
            }}
            onBlur={formik.handleBlur}
            error={formik.touched.username && formik.errors.username}
          />

          <label>Correo electrónico</label>
          <Form.Input
            name="email"
            placeholder="Correo electrónico"
            autoComplete="email"
            value={formik.values.email}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.email && formik.errors.email}
          />

          <label>Contraseña</label>
          <Form.Input
            name="password"
            type="password"
            placeholder="Contraseña"
            autoComplete="new-password"
            value={formik.values.password}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={formik.touched.password && formik.errors.password}
          />

          <label>Confirmar Contraseña</label>
          <Form.Input
            name="password_confirm"
            type="password"
            placeholder="Confirmar Contraseña"
            autoComplete="new-password"
            value={formik.values.password_confirm}
            onChange={formik.handleChange}
            onBlur={formik.handleBlur}
            error={
              formik.touched.password_confirm && formik.errors.password_confirm
            }
          />

          <Button
            type="submit"
            content="Registrarme"
            primary
            fluid
            loading={formik.isSubmitting}
          />
        </Form>

        <p className="register-admin__link">
          ¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link>
        </p>
      </div>
    </div>
  );
}

function initialValues() {
  return {
    username: "",
    email: "",
    password: "",
    password_confirm: "",
  };
}

function validationSchema() {
  return Yup.object({
    username: Yup.string()
      .required("El usuario es obligatorio")
      .matches(/^\S*$/, "El usuario no debe contener espacios"),
    email: Yup.string()
      .email("Correo electrónico no válido")
      .required("El correo electrónico es obligatorio"),
    password: Yup.string()
      .required("La contraseña es obligatoria")
      .min(8, "La contraseña debe tener al menos 8 caracteres")
      .matches(/[A-Z]/, "La contraseña debe contener al menos una letra mayúscula")
      .matches(/\d/, "La contraseña debe contener al menos un número")
      .matches(
        /[@$!%*?&#]/,
        "La contraseña debe contener al menos un carácter especial (@$!%*?&#)"
      ),
    password_confirm: Yup.string()
      .required("La confirmación de contraseña es obligatoria")
      .oneOf([Yup.ref("password")], "Las contraseñas no coinciden"),
  });
}
