import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { MapPin, Coffee } from 'lucide-react'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    const result = await login(email, password)
    
    if (!result.success) {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md space-y-8">
        {/* Logo e Header */}
        <div className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="bg-primary rounded-full p-3">
              <MapPin className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900">Taiglo</h1>
          </div>
          <p className="text-gray-600">Descubra experiências únicas em São Paulo</p>
        </div>

        {/* Card de Login */}
        <Card>
          <CardHeader>
            <CardTitle>Entrar na sua conta</CardTitle>
            <CardDescription>
              Entre com suas credenciais para acessar o Taiglo
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="seu@email.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="password">Senha</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Sua senha"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              
              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading}
              >
                {loading ? 'Entrando...' : 'Entrar'}
              </Button>
            </form>
            
            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                Não tem uma conta?{' '}
                <Link 
                  to="/register" 
                  className="font-medium text-primary hover:underline"
                >
                  Registre-se
                </Link>
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Conta de Teste */}
        {/* <Card className="bg-amber-50 border-amber-200">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 mb-2">
              <Coffee className="h-4 w-4 text-amber-600" />
              <h3 className="font-medium text-amber-800">Conta de Teste</h3>
            </div>
            <p className="text-sm text-amber-700 mb-3">
              Use estas credenciais para testar o sistema:
            </p>
            <div className="text-xs text-amber-600 space-y-1">
              <p><strong>Email:</strong> teste@taiglo.com</p>
              <p><strong>Senha:</strong> senha123</p>
            </div>
          </CardContent>
        </Card>*/}
      </div>
    </div>
  )
}

