subroutine axpy_f(n, a, x, y, out) bind(C, name="axpy_f")
  use iso_c_binding, only: c_int, c_double
  implicit none

  integer(c_int), intent(in) :: n
  real(c_double), intent(in) :: a
  real(c_double), intent(in) :: x(*)
  real(c_double), intent(in) :: y(*)
  real(c_double), intent(out) :: out(*)
  integer(c_int) :: i

  do i = 1, n
    out(i) = a * x(i) + y(i)
  end do
end subroutine axpy_f
